import streamlit as st

from utils.data_loader import init_sqlite, run_sql
from utils.app_style import content_section, page_header, spacer

page_header(
    "SQL Analytics",
    "Ten business questions on an in-memory SQLite table. All amounts are in Indian Rupees (₹).",
    tag="Business Intelligence",
)

conn = init_sqlite()

QUERIES = [
    {
        "title": "1. Top 10 Highest Claim Customers",
        "purpose": "Identify largest single payouts for executive review.",
        "sql": """
SELECT CustomerAge, AnnualIncome, PolicyType, ClaimAmount, FraudRisk
FROM insurance_claims
ORDER BY ClaimAmount DESC
LIMIT 10;
""",
    },
    {
        "title": "2. Average Premium by Policy Type",
        "purpose": "Compare pricing across product lines.",
        "sql": """
SELECT PolicyType,
       ROUND(AVG(PremiumAmount), 2) AS AvgPremium
FROM insurance_claims
GROUP BY PolicyType
ORDER BY AvgPremium DESC;
""",
    },
    {
        "title": "3. Total Fraud-Risk Claims",
        "purpose": "Count claims flagged for investigation.",
        "sql": """
SELECT COUNT(*) AS TotalFraudRiskClaims
FROM insurance_claims
WHERE FraudRisk = 1;
""",
    },
    {
        "title": "4. Average Claim Amount by Age Group",
        "purpose": "Segment loss by Youth / Middle-Age / Senior cohorts.",
        "sql": """
SELECT
    CASE
        WHEN CustomerAge < 30 THEN 'Youth'
        WHEN CustomerAge BETWEEN 30 AND 50 THEN 'Middle-Age'
        ELSE 'Senior'
    END AS AgeGroup,
    ROUND(AVG(ClaimAmount), 2) AS AvgClaimAmount,
    COUNT(*) AS ClaimCount
FROM insurance_claims
GROUP BY AgeGroup
ORDER BY AvgClaimAmount DESC;
""",
    },
    {
        "title": "5. Policy Type with Highest Total Claim Amount",
        "purpose": "Find the costliest product line in aggregate.",
        "sql": """
SELECT PolicyType,
       ROUND(SUM(ClaimAmount), 2) AS TotalClaimAmount
FROM insurance_claims
GROUP BY PolicyType
ORDER BY TotalClaimAmount DESC
LIMIT 1;
""",
    },
    {
        "title": "6. Customers with More Than 3 Previous Claims",
        "purpose": "Flag high-frequency claimants.",
        "sql": """
SELECT CustomerAge, PolicyType, PreviousClaims, ClaimAmount, FraudRisk
FROM insurance_claims
WHERE PreviousClaims > 3
ORDER BY PreviousClaims DESC;
""",
    },
    {
        "title": "7. Highest Hospital Expense Customers",
        "purpose": "Medical cost outliers (Health policies).",
        "sql": """
SELECT CustomerAge, PolicyType, HospitalExpense, ClaimAmount, FraudRisk
FROM insurance_claims
WHERE HospitalExpense > 0
ORDER BY HospitalExpense DESC
LIMIT 15;
""",
    },
    {
        "title": "8. Average Claim Duration by Policy Type",
        "purpose": "Operational KPI — processing time by line.",
        "sql": """
SELECT PolicyType,
       ROUND(AVG(ClaimDuration), 2) AS AvgClaimDurationDays
FROM insurance_claims
GROUP BY PolicyType
ORDER BY AvgClaimDurationDays DESC;
""",
    },
    {
        "title": "9. Total Premium Collected",
        "purpose": "Top-line revenue from premiums in the portfolio.",
        "sql": """
SELECT ROUND(SUM(PremiumAmount), 2) AS TotalPremiumCollected
FROM insurance_claims;
""",
    },
    {
        "title": "10. Fraud-Risk Percentage Overall",
        "purpose": "Portfolio-wide fraud exposure rate.",
        "sql": """
SELECT
    SUM(FraudRisk) AS FraudClaims,
    COUNT(*) AS TotalClaims,
    ROUND(100.0 * AVG(FraudRisk), 2) AS FraudRiskPercent
FROM insurance_claims;
""",
    },
]

with content_section("Business questions"):
    with st.spinner("Running queries..."):
        for q in QUERIES:
            with st.expander(q["title"], expanded=False):
                st.caption(q["purpose"])
                st.code(q["sql"].strip(), language="sql")
                try:
                    result = run_sql(q["sql"], conn)
                    st.dataframe(result, use_container_width=True, hide_index=True)
                except Exception as e:
                    st.error(f"Query failed: {e}")

spacer("md")

with content_section("Indexes & views (SQL Server design)"):
    st.markdown(
        "The capstone SQL Server layer (`INDEXES_VIEWS.sql`, `DBModelling_Migration.sql`) "
        "includes the objects below. SQLite analogs are shown where applicable."
    )

with st.expander("Revenue & Market Performance"):
    st.markdown(
        """
        - **`IX_Customers_Age_Income`** — speeds age/income filters and joins.
        - **`vw_PremiumMetricsByType`** — policy counts, avg & total premium by type.
        - **`vw_PremiumGrowthTrend`** — cumulative revenue via window functions.
        - **`proc_GetRevenuePerformanceMetrics`** — hub proc for finance dashboards.
        """
    )
    st.code(
        """SELECT PolicyType, COUNT(*) AS PolicyCount,
       AVG(PremiumAmount) AS AvgPremium, SUM(PremiumAmount) AS TotalPremium
FROM insurance_claims GROUP BY PolicyType;""",
        language="sql",
    )
    st.dataframe(run_sql(
        "SELECT PolicyType, COUNT(*) AS PolicyCount, "
        "ROUND(AVG(PremiumAmount),2) AS AvgPremium, "
        "ROUND(SUM(PremiumAmount),2) AS TotalPremium "
        "FROM insurance_claims GROUP BY PolicyType;", conn
    ), hide_index=True)

with st.expander("Risk & Fraud Governance"):
    st.markdown(
        """
        - **`CSI_Claims_Analytics`** (columnstore) — fast aggregations on claim facts.
        - **`vw_FraudRiskExposure`** — counts and % by fraud flag.
        - **`vw_FrequentClaimants`** — customers with >3 claims.
        """
    )
    st.code(
        """SELECT FraudRisk, COUNT(*) AS TotalClaims,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS RiskPct
FROM insurance_claims GROUP BY FraudRisk;""",
        language="sql",
    )
    st.dataframe(run_sql(
        "SELECT FraudRisk, COUNT(*) AS TotalClaims, "
        "ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS RiskPct "
        "FROM insurance_claims GROUP BY FraudRisk;", conn
    ), hide_index=True)

with st.expander("Claims Analytics & Loss Ratios"):
    st.markdown(
        "- **`vw_Top10HighValueClaimants`** — DENSE_RANK top payouts.\n"
        "- **`vw_PolicyTypeLossRatio`** — total and peak claim by policy type.\n"
        "- **`vw_HighHospitalExpenseAnalytics`** — hospital cost percentiles."
    )

with st.expander("Demographic Insights"):
    st.markdown(
        "- **`vw_AgeGroupClaimAnalysis`** — youth / middle / senior segments.\n"
        "- **`vw_IncomeBracketRiskProfile`** — claims by income bracket.\n"
        "- **`vw_SeniorHighValueAnalysis`** — senior lifetime claim value."
    )

with st.expander("Operational Efficiency"):
    st.markdown(
        """
        - **`vw_ClaimOperationalEfficiency`** — avg duration by policy type.
        - **`vw_AnnualOperationalThroughput`** — claims per year, man-days.
        - **`pf_ClaimDate` / `ps_ClaimDate`** — partition scheme for annual throughput.
        """
    )
    st.code(
        """SELECT CAST(strftime('%Y', ClaimDate) AS INT) AS ClaimYear,
       COUNT(*) AS ClaimsProcessed,
       ROUND(AVG(ClaimDuration), 2) AS AvgDuration
FROM insurance_claims GROUP BY ClaimYear ORDER BY ClaimYear;""",
        language="sql",
    )
    st.dataframe(run_sql(
        "SELECT CAST(strftime('%Y', ClaimDate) AS INT) AS ClaimYear, "
        "COUNT(*) AS ClaimsProcessed, ROUND(AVG(ClaimDuration), 2) AS AvgDuration "
        "FROM insurance_claims GROUP BY ClaimYear ORDER BY ClaimYear;", conn
    ), hide_index=True)
