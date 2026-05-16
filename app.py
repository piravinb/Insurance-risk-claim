"""Insurance Claim Risk & Customer Analysis — Streamlit entry point."""

import streamlit as st

from utils.app_style import apply_theme, render_logo, render_sidebar
from utils.data_loader import CSV_PATH, dataset_exists

st.set_page_config(
    page_title="Insurance Claim Risk Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_theme()
render_sidebar()
render_logo()

if not dataset_exists():
    st.error(
        f"Dataset not found at `{CSV_PATH}`. "
        "Please add `realistic_insurance_claim_dataset.csv` to the app folder."
    )
    st.stop()

pages = [
    st.Page("pages/1_Home.py", title="Home", icon="🏠", default=True),
    st.Page("pages/2_Dataset_Overview.py", title="Dataset Overview", icon="📦"),
    st.Page("pages/3_EDA.py", title="EDA", icon="📊"),
    st.Page("pages/4_SQL_Analytics.py", title="SQL Analytics", icon="🗄️"),
    st.Page(
        "pages/5_Linear_Regression.py",
        title="Claim Prediction",
        icon="📈",
    ),
    st.Page(
        "pages/6_Logistic_Regression.py",
        title="Fraud Detection",
        icon="🚨",
    ),
    st.Page("pages/7_Live_Predictor.py", title="Live Predictor", icon="🔮"),
    st.Page("pages/8_Business_Insights.py", title="Business Insights", icon="💡"),
]

st.navigation(pages).run()
