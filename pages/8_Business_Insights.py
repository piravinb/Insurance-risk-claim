import pandas as pd
import streamlit as st

from utils.app_style import content_section, format_inr, page_header, spacer
from utils.data_loader import init_sqlite, load_dataset, run_sql
from utils.model_trainer import train_or_load_models

page_header(
    "Business Insights & Recommendations",
    "Executive summary, actionable recommendations, and model performance at a glance.",
    tag="Strategy",
)

df = load_dataset()
conn = init_sqlite()
meta = train_or_load_models()

fraud_pct = 100 * df["FraudRisk"].mean()
top_policy = df.groupby("PolicyType")["ClaimAmount"].sum().idxmax()
high_prev = (df["PreviousClaims"] > 3).sum()
long_duration = (df["ClaimDuration"] > 45).sum()

with content_section("Key findings"):
    fc1, fc2, fc3, fc4 = st.columns(4)
    fc1.metric("Portfolio fraud rate", f"{fraud_pct:.1f}%")
    fc2.metric("Costliest policy line", top_policy)
    fc3.metric("High-frequency claimants (>3)", f"{high_prev:,}")
    fc4.metric("Long duration claims (>45d)", f"{long_duration:,}")

recommendations = [
    (
        "**Strengthen fraud triage for high-frequency claimants.** "
        f"{high_prev} records have more than 3 previous claims."
    ),
    (
        "**Monitor claims over 45 days duration.** "
        f"{long_duration} claims exceed this threshold — a known fraud red flag."
    ),
    (
        f"**Review loss concentration on {top_policy} policies.** "
        "Highest total claim amount by product line."
    ),
    (
        f"**Use regression for reserve planning** ({meta['best_regression_model']}, "
        f"OOF R² {meta['regression']['oof_r2']:.2f})."
    ),
    (
        f"**Deploy fraud model as ranking** (AUC {meta['classification']['avg_auc']:.2f}) — "
        "not auto-deny; investigators review top scores."
    ),
    (
        "**Enforce policy limits at FNOL** — many claims approach `InsuredAmount`."
    ),
    (
        "**Segment by age cohort** — Youth, Middle-Age, and Senior show different severities."
    ),
]

with content_section("Recommendations"):
    for i, rec in enumerate(recommendations, 1):
        st.markdown(f"{i}. {rec}")

reg = meta["regression"]
clf = meta["classification"]

with content_section("Model metrics summary"):
    summary = pd.DataFrame([
        {
            "Model": meta["best_regression_model"],
            "Task": "Claim Amount",
            "MAE": format_inr(reg["avg_mae"]),
            "RMSE": format_inr(reg["avg_rmse"]),
            "R² (CV)": f"{reg['avg_r2']:.3f}",
            "R² (OOF)": f"{reg['oof_r2']:.3f}",
            "AUC": "—",
        },
        {
            "Model": "LogisticRegression",
            "Task": "Fraud Risk",
            "MAE": "—",
            "RMSE": "—",
            "R² (CV)": "—",
            "R² (OOF)": "—",
            "AUC": f"{clf['avg_auc']:.3f}",
        },
    ])
    st.dataframe(summary, use_container_width=True, hide_index=True)

premium_total = run_sql(
    "SELECT ROUND(SUM(PremiumAmount), 2) AS TotalPremium FROM insurance_claims", conn
).iloc[0, 0]
claim_total = run_sql(
    "SELECT ROUND(SUM(ClaimAmount), 2) AS TotalClaims FROM insurance_claims", conn
).iloc[0, 0]

with content_section("Conclusion"):
    st.markdown(
        f"""
        This capstone analyzes **{len(df):,} policies** through SQL, EDA, and ML.
        Premium collected totals **{format_inr(premium_total)}** against **{format_inr(claim_total)}**
        in claims — underscoring disciplined underwriting, fraud governance, and
        data-driven pricing. Use the **Live Predictor** for what-if scoring in demos.
        """
    )
