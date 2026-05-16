import streamlit as st

from utils.data_loader import get_column_info, load_dataset
from utils.app_style import content_section, insight, page_header, spacer

page_header(
    "Dataset Overview",
    "Structure, quality checks, and summary statistics for the insurance claims portfolio.",
    tag="Data",
)

with st.spinner("Loading dataset..."):
    df = load_dataset()

with content_section("At a glance"):
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Rows", f"{len(df):,}")
    c2.metric("Total Columns", len(df.columns))
    c3.metric("Missing Values", int(df.isnull().sum().sum()))

spacer("sm")

insight(
    "**Currency:** All monetary fields (`AnnualIncome`, `PremiumAmount`, `ClaimAmount`, "
    "`HospitalExpense`, `InsuredAmount`) are in **Indian Rupees (₹)**."
)
insight(
    "**New columns (beyond original spec):** `PolicyStartDate`, `ClaimDate`, and "
    "`InsuredAmount` support temporal analysis, policy limits, and feature engineering."
)

with content_section("Column dictionary"):
    st.dataframe(get_column_info(df), use_container_width=True, hide_index=True)

with content_section("Sample records"):
    st.dataframe(df.head(10), use_container_width=True)

with content_section("Data types"):
    st.dataframe(
        df.dtypes.astype(str).reset_index().rename(columns={"index": "Column", 0: "Type"}),
        use_container_width=True,
        hide_index=True,
    )

with content_section("Missing values"):
    missing = df.isnull().sum().reset_index()
    missing.columns = ["Column", "Missing Count"]
    st.dataframe(missing, use_container_width=True, hide_index=True)

with content_section("Numeric summary"):
    st.dataframe(df.describe().T, use_container_width=True)
