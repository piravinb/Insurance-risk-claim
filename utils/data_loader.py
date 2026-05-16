"""CSV loading, feature engineering, and SQLite analytics."""

from pathlib import Path

import pandas as pd
import sqlite3
import streamlit as st

APP_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = APP_DIR / "realistic_insurance_claim_dataset.csv"

DATE_COLUMNS = ["PolicyStartDate", "ClaimDate"]
NEW_COLUMNS = ["PolicyStartDate", "ClaimDate", "InsuredAmount"]

COLUMN_DESCRIPTIONS = {
    "CustomerAge": "Customer age in years (18–60 in source data).",
    "AnnualIncome": "Annual income in Indian Rupees (₹).",
    "PolicyType": "Insurance line: Health, Vehicle, Life, or Travel.",
    "PolicyStartDate": "Date the policy became active (added beyond original spec).",
    "ClaimDate": "Date the claim was filed (added beyond original spec).",
    "InsuredAmount": "Sum insured / policy limit in ₹ (added beyond original spec).",
    "PremiumAmount": "Premium paid for the policy in ₹.",
    "PreviousClaims": "Count of prior claims by the customer.",
    "ClaimDuration": "Claim processing duration in days.",
    "HospitalExpense": "Hospital costs in ₹ (Health policies; 0 otherwise).",
    "VehicleAge": "Vehicle age in years (Vehicle policies; 0 otherwise).",
    "ClaimAmount": "Target: payout amount for the claim in ₹.",
    "FraudRisk": "Target: 1 = high fraud risk, 0 = low risk.",
    "DaysSincePolicyStart": "Engineered: days between policy start and claim date.",
}


def dataset_exists() -> bool:
    return CSV_PATH.exists()


@st.cache_data(show_spinner="Loading dataset...")
def load_dataset() -> pd.DataFrame:
    if not dataset_exists():
        raise FileNotFoundError(f"Dataset not found: {CSV_PATH}")
    df = pd.read_csv(CSV_PATH)
    for col in DATE_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col])
    return df


@st.cache_data(show_spinner="Preparing features...")
def get_processed_df() -> pd.DataFrame:
    df = load_dataset().copy()
    if "PolicyStartDate" in df.columns and "ClaimDate" in df.columns:
        df["DaysSincePolicyStart"] = (df["ClaimDate"] - df["PolicyStartDate"]).dt.days
        df["DaysSincePolicyStart"] = df["DaysSincePolicyStart"].clip(lower=0)
    return df


@st.cache_resource(show_spinner="Initializing SQLite...")
def init_sqlite() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    df = load_dataset()
    export = df.copy()
    for col in DATE_COLUMNS:
        if col in export.columns:
            export[col] = export[col].dt.strftime("%Y-%m-%d")
    export.to_sql("insurance_claims", conn, index=False, if_exists="replace")
    return conn


def run_sql(query: str, conn: sqlite3.Connection | None = None) -> pd.DataFrame:
    if conn is None:
        conn = init_sqlite()
    return pd.read_sql_query(query, conn)


def get_column_info(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col in df.columns:
        rows.append(
            {
                "Column": col,
                "Type": str(df[col].dtype),
                "Missing": int(df[col].isnull().sum()),
                "Description": COLUMN_DESCRIPTIONS.get(col, ""),
            }
        )
    return pd.DataFrame(rows)
