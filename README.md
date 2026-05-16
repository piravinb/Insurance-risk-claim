# Insurance Claim Risk & Customer Analysis

Streamlit capstone application for insurance claim analytics, SQL business intelligence, and machine learning (claim amount regression + fraud classification).

## Setup

```bash
cd InsuranceClaimRisk
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run locally

```bash
streamlit run app.py
```

## Deploy on Streamlit Community Cloud

1. Push this repo to GitHub: [piravinb/Insurance-risk-claim](https://github.com/piravinb/Insurance-risk-claim)
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**
3. Repository: `piravinb/Insurance-risk-claim`, branch: `main`
4. **Main file path:** `app.py`
5. Click **Deploy**

Pre-trained models in `models/` are included so the app loads quickly without retraining on first visit.

## Dataset

Place `realistic_insurance_claim_dataset.csv` in this folder (included). Columns:

`CustomerAge`, `AnnualIncome`, `PolicyType`, `PolicyStartDate`, `ClaimDate`, `InsuredAmount`, `PremiumAmount`, `PreviousClaims`, `ClaimDuration`, `HospitalExpense`, `VehicleAge`, `ClaimAmount`, `FraudRisk`

## Models

On first visit to ML pages, models train automatically and save to `models/`:

- `regression_model.joblib` + `regression_preprocessor.joblib`
- `logistic_model.joblib` + `logistic_preprocessor.joblib`
- `regression_metadata.json`

Use **Rebuild ML models** in the sidebar to clear cache and retrain.

## Notes

- SQL pages use in-memory SQLite (flat table), not SQL Server.
- Regression follows `ML.py`: Ridge / Decision Tree / XGBoost with 5-fold CV; best model is saved.
- Fraud model: Logistic Regression + SMOTE; `ClaimAmount` excluded from features.
- Live Predictor uses `DaysSincePolicyStart` slider instead of raw dates.

## Project structure

```
app.py              # Entry + global theme
pages/              # Multi-page Streamlit UI
utils/              # Data, charts, ML training
models/             # Saved joblib artifacts (generated)
```

Parent folder retains original capstone scripts (`ML.py`, SQL files, `data_generation.py`).
