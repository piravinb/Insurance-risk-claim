import numpy as np
import pandas as pd
import streamlit as st

from utils.app_style import content_section, format_inr, insight, page_header, spacer
from utils.charts import bar_count, correlation_heatmap, histogram, pie_chart
from utils.model_trainer import get_full_model_bundle

REQUIRED_COLUMNS = [
    "CustomerAge",
    "AnnualIncome",
    "PolicyType",
    "PremiumAmount",
    "PreviousClaims",
    "ClaimDuration",
    "HospitalExpense",
    "VehicleAge",
    "InsuredAmount",
    "ClaimAmount",
    "FraudRisk",
]

NUMERIC_COLUMNS = [
    "CustomerAge",
    "AnnualIncome",
    "PremiumAmount",
    "PreviousClaims",
    "ClaimDuration",
    "HospitalExpense",
    "VehicleAge",
    "InsuredAmount",
    "ClaimAmount",
    "FraudRisk",
]

DEFAULT_DAYS_SINCE_START = 400


page_header(
    "Dynamic Data Pipeline",
    "Upload your own CSV and run EDA plus ML predictions on the trained models.",
    tag="Custom Data",
)

with content_section("Step 1 — CSV upload"):
    st.markdown(
        "Your CSV **must** contain these columns (extra columns are ignored):\n\n"
        + ", ".join(f"`{c}`" for c in REQUIRED_COLUMNS)
    )
    st.info("Extra columns are allowed but will be ignored.")
    uploaded = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded is None:
    st.stop()

try:
    df_upload = pd.read_csv(uploaded)
except Exception as e:
    st.error(f"Could not read CSV: {e}")
    st.stop()

missing = [c for c in REQUIRED_COLUMNS if c not in df_upload.columns]

with content_section("Step 2 — Column validation"):
    if missing:
        st.error(
            "**Missing required columns:** "
            + ", ".join(f"`{c}`" for c in missing)
        )
        st.warning("Please fix your CSV and re-upload.")
        st.stop()

    st.success("✅ All required columns found! Running pipeline...")

    type_errors = []
    for col in NUMERIC_COLUMNS:
        converted = pd.to_numeric(df_upload[col], errors="coerce")
        if converted.isna().any():
            type_errors.append(col)
    if not (
        pd.api.types.is_string_dtype(df_upload["PolicyType"])
        or df_upload["PolicyType"].dtype == object
    ):
        type_errors.append("PolicyType (expected text)")

    if type_errors:
        st.warning(
            "Some columns could not be validated as the expected type: "
            + ", ".join(f"`{c}`" for c in type_errors)
        )
    else:
        st.caption("Data types look valid — numeric fields are numeric; PolicyType is text.")

    st.markdown("**Preview (first 5 rows)**")
    st.dataframe(df_upload.head(5), use_container_width=True, hide_index=True)

df_work = df_upload.copy()
for col in NUMERIC_COLUMNS:
    df_work[col] = pd.to_numeric(df_work[col], errors="coerce")

with content_section("Step 3 — EDA on uploaded data"):
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(
            histogram(df_work, "ClaimAmount", "Claim Amount Distribution"),
            use_container_width=True,
        )
        insight(
            f"Mean claim amount is **{format_inr(df_work['ClaimAmount'].mean())}**; "
            "distribution shape guides severity expectations."
        )
    with c2:
        st.plotly_chart(
            bar_count(df_work, "PolicyType", "Policy Type Distribution"),
            use_container_width=True,
        )
        top_type = df_work["PolicyType"].value_counts().idxmax()
        insight(f"**{top_type}** is the most common policy type in this upload.")

    spacer("sm")
    c3, c4 = st.columns(2)
    with c3:
        st.plotly_chart(pie_chart(df_work, "FraudRisk", "Fraud Risk Distribution"), use_container_width=True)
        fraud_pct = 100 * df_work["FraudRisk"].mean()
        insight(f"**{fraud_pct:.1f}%** of rows are flagged as high fraud risk (FraudRisk = 1).")
    with c4:
        st.plotly_chart(correlation_heatmap(df_work), use_container_width=True)
        insight("Correlations highlight which numeric features move together with claim amount.")

with content_section("Step 4 — ML predictions on uploaded data"):
    with st.spinner("Loading models and scoring rows..."):
        reg_model, reg_pre, clf_model, clf_pre, metadata = get_full_model_bundle()

    features = metadata["regression_features"]
    prepared = df_work.copy()

    if "PolicyStartDate" in prepared.columns and "ClaimDate" in prepared.columns:
        prepared["PolicyStartDate"] = pd.to_datetime(prepared["PolicyStartDate"])
        prepared["ClaimDate"] = pd.to_datetime(prepared["ClaimDate"])
        prepared["DaysSincePolicyStart"] = (
            prepared["ClaimDate"] - prepared["PolicyStartDate"]
        ).dt.days.clip(lower=0)
    else:
        prepared["DaysSincePolicyStart"] = DEFAULT_DAYS_SINCE_START

    drop_cols = ["PolicyStartDate", "ClaimDate", "ClaimAmount", "FraudRisk"]
    X = prepared.drop(columns=[c for c in drop_cols if c in prepared.columns], errors="ignore")
    for feat in features:
        if feat not in X.columns:
            X[feat] = 0
    X = X[features]

    claim_preds = reg_model.predict(reg_pre.transform(X))
    fraud_proba = clf_model.predict_proba(clf_pre.transform(X))[:, 1]
    fraud_preds = (fraud_proba >= 0.5).astype(int)

    df_reg = df_upload.copy()
    df_reg["Predicted_ClaimAmount"] = claim_preds

    df_clf = df_upload.copy()
    df_clf["Predicted_FraudRisk"] = fraud_preds
    df_clf["Fraud_Probability"] = np.round(fraud_proba, 4)

    df_results = df_upload.copy()
    df_results["Predicted_ClaimAmount"] = claim_preds
    df_results["Predicted_FraudRisk"] = fraud_preds
    df_results["Fraud_Probability"] = np.round(fraud_proba, 4)

    t1, t2 = st.columns(2)
    with t1:
        st.markdown("**Claim amount predictions**")
        st.dataframe(df_reg, use_container_width=True, hide_index=True)
    with t2:
        st.markdown("**Fraud risk predictions**")
        st.dataframe(df_clf, use_container_width=True, hide_index=True)

    avg_claim = float(np.mean(claim_preds))
    high_risk_count = int(fraud_preds.sum())
    fraud_pct = 100.0 * high_risk_count / len(fraud_preds) if len(fraud_preds) else 0.0

    m1, m2, m3 = st.columns(3)
    m1.metric("Avg predicted claim", format_inr(avg_claim))
    m2.metric("High-risk fraud cases", f"{high_risk_count:,}")
    m3.metric("Fraud risk %", f"{fraud_pct:.1f}%")

with content_section("Step 5 — Download results"):
    csv_bytes = df_results.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Results as CSV",
        data=csv_bytes,
        file_name="pipeline_predictions.csv",
        mime="text/csv",
        type="primary",
        use_container_width=True,
    )
