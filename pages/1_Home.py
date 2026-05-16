import streamlit as st

from utils.app_style import content_section, page_header, spacer, tech_pills

page_header(
    "Insurance Claim Risk & Customer Analysis",
    "Analytics and machine learning platform for claims intelligence and fraud detection.",
    tag="Capstone Project",
)

with content_section("Problem Statement"):
    st.markdown(
        """
        Insurance companies face rising claim volumes, uneven fraud exposure, and slow,
        fragmented reporting. Leadership needs a unified view of **who claims most**,
        **which policy types drive loss**, and **which claims warrant fraud review** — while
        actuaries need reliable estimates of future claim severity.
        """
    )

spacer("md")

with content_section("Solution Overview"):
    st.markdown(
        """
        We built an end-to-end system that:
        - Ingests and validates **2,000** realistic customer and claim records
        - Runs SQL analytics with indexes, views, and business queries
        - Surfaces patterns through interactive dashboards
        - Predicts **claim amounts** (best regression model, 5-fold CV)
        - Flags **fraud risk** (logistic regression with SMOTE)
        - Powers a **live predictor** for stakeholder demos
        """
    )

spacer("md")

with content_section("Tech Stack"):
    tech_pills([
        "Python", "Pandas", "SQLite", "SQL Server", "Scikit-learn",
        "XGBoost", "imbalanced-learn", "Plotly", "Streamlit", "Joblib",
    ])

spacer("md")

with content_section("Project Flow"):
    st.markdown(
        """
        **CSV Dataset** → Validation → **SQLite / SQL Analytics**

        ↓

        **EDA** → Feature engineering (`DaysSincePolicyStart`)

        ↓

        **Regression** + **Fraud classification**

        ↓

        **Live Predictor** → **Business insights**
        """
    )
