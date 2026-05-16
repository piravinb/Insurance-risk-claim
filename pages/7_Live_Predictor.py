import streamlit as st

from utils.app_style import content_section, format_inr, page_header, spacer
from utils.data_loader import get_processed_df
from utils.model_trainer import (
    get_full_model_bundle,
    predict_claim_amount,
    predict_fraud,
)

page_header(
    "Live Predictor",
    "Score a new claim for expected payout and fraud risk in real time.",
    tag="Interactive",
)

df = get_processed_df()
median_tenure = int(df["DaysSincePolicyStart"].median()) if "DaysSincePolicyStart" in df.columns else 400
median_income = int(df["AnnualIncome"].median())
median_premium = int(df["PremiumAmount"].median())
median_insured = int(df["InsuredAmount"].median())
median_hospital = (
    int(df[df["HospitalExpense"] > 0]["HospitalExpense"].median())
    if (df["HospitalExpense"] > 0).any()
    else 150000
)

with content_section("Enter claim details"):
    with st.form("predictor_form"):
        c1, c2 = st.columns(2)
        with c1:
            customer_age = st.slider("Customer Age", 18, 70, 40)
            annual_income = st.number_input(
                "Annual Income", min_value=50_000, max_value=5_000_000,
                value=median_income, step=10_000,
            )
            policy_type = st.selectbox("Policy Type", ["Health", "Vehicle", "Life", "Travel"])
            premium_amount = st.number_input(
                "Premium Amount", min_value=1_000, max_value=200_000,
                value=median_premium, step=500,
            )
            insured_amount = st.number_input(
                "Insured Amount", min_value=10_000, max_value=30_000_000,
                value=median_insured, step=10_000,
            )
        with c2:
            previous_claims = st.slider("Previous Claims", 0, 8, 1)
            claim_duration = st.slider("Claim Duration (days)", 1, 90, 18)
            hospital_expense = st.number_input(
                "Hospital Expense", min_value=0, max_value=1_000_000,
                value=median_hospital, step=5_000,
            )
            vehicle_age = st.slider("Vehicle Age", 0, 15, 5)
            days_since_start = st.slider(
                "Days Since Policy Start", 1, 900, median_tenure,
                help="Engineered feature used instead of raw dates in the ML pipeline.",
            )

        col_a, col_b = st.columns(2)
        with col_a:
            submitted_claim = st.form_submit_button(
                "Predict Claim Amount", type="primary", use_container_width=True,
            )
        with col_b:
            submitted_fraud = st.form_submit_button(
                "Check Fraud Risk", use_container_width=True,
            )

raw = {
    "CustomerAge": customer_age,
    "AnnualIncome": annual_income,
    "PolicyType": policy_type,
    "PremiumAmount": premium_amount,
    "InsuredAmount": insured_amount,
    "PreviousClaims": previous_claims,
    "ClaimDuration": claim_duration,
    "HospitalExpense": hospital_expense if policy_type == "Health" else 0,
    "VehicleAge": vehicle_age if policy_type == "Vehicle" else 0,
    "DaysSincePolicyStart": days_since_start,
}

if submitted_claim or submitted_fraud:
    with st.spinner("Running models..."):
        reg_model, reg_pre, clf_model, clf_pre, meta = get_full_model_bundle()

    spacer("sm")

    if submitted_claim:
        with content_section("Claim amount prediction"):
            amount = predict_claim_amount(reg_model, reg_pre, raw)
            st.markdown(
                f'<div class="prediction-box">Predicted Claim Amount: {format_inr(amount, 2)}</div>',
                unsafe_allow_html=True,
            )
            st.caption(f"Model: {meta['best_regression_model']}")

    if submitted_fraud:
        with content_section("Fraud risk assessment"):
            label, proba = predict_fraud(clf_model, clf_pre, raw)
            if label == 1:
                st.markdown(
                    f'<div class="risk-high">HIGH RISK — Flagged for fraud review<br>'
                    f'<span style="font-size:0.95rem;">Probability: {proba:.1%}</span></div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<div class="risk-low">LOW RISK — Appears legitimate<br>'
                    f'<span style="font-size:0.95rem;">Probability of fraud: {proba:.1%}</span></div>',
                    unsafe_allow_html=True,
                )

spacer("sm")
st.caption("Rebuild models from the sidebar after refreshing the dataset.")
