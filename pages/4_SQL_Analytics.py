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

SQL_VIEWS = [
    {
        "category": "Revenue & Market Performance",
        "items": [
            {
                "name": "vw_PremiumMetricsByType",
                "purpose": "Policy counts, average premium, and total premium collected by policy type.",
                "ddl": """
CREATE VIEW vw_PremiumMetricsByType AS
SELECT
    PolicyType AS TypeName,
    COUNT(*) AS PolicyCount,
    ROUND(AVG(PremiumAmount), 2) AS AvgPremium,
    ROUND(SUM(PremiumAmount), 2) AS TotalPremiumCollected
FROM insurance_claims
GROUP BY PolicyType;
""",
            },
            {
                "name": "vw_PremiumGrowthTrend",
                "purpose": "Running total of premium revenue ordered by policy start date.",
                "ddl": """
CREATE VIEW vw_PremiumGrowthTrend AS
SELECT
    PolicyStartDate AS StartDate,
    PremiumAmount,
    SUM(PremiumAmount) OVER (ORDER BY PolicyStartDate) AS CumulativeRevenue
FROM insurance_claims;
""",
            },
        ],
    },
    {
        "category": "Risk & Fraud Governance",
        "items": [
            {
                "name": "vw_FraudMasterDashboard",
                "purpose": "Fraud analyst dashboard: claim size vs income and prior-claim history.",
                "ddl": """
CREATE VIEW vw_FraudMasterDashboard AS
SELECT
    rowid AS ClaimID,
    CustomerAge,
    AnnualIncome,
    ClaimAmount,
    PreviousClaims,
    FraudRisk,
    CASE
        WHEN ClaimAmount > (AnnualIncome * 0.5) THEN 1
        ELSE 0
    END AS IsClaimExceedingHalfIncome
FROM insurance_claims;
""",
            },
            {
                "name": "vw_FraudRiskExposure",
                "purpose": "Portfolio exposure: claim counts, potential loss, and fraud percentage by risk flag.",
                "ddl": """
CREATE VIEW vw_FraudRiskExposure AS
SELECT
    FraudRisk,
    COUNT(*) AS TotalClaims,
    ROUND(SUM(ClaimAmount), 2) AS TotalPotentialLoss,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS RiskPercentage
FROM insurance_claims
GROUP BY FraudRisk;
""",
            },
            {
                "name": "vw_FrequentClaimants",
                "purpose": "Claims where the customer has more than three previous claims (high-frequency flag).",
                "ddl": """
CREATE VIEW vw_FrequentClaimants AS
SELECT
    CustomerAge,
    PolicyType,
    PreviousClaims,
    ClaimAmount,
    FraudRisk
FROM insurance_claims
WHERE PreviousClaims > 3
ORDER BY PreviousClaims DESC;
""",
            },
        ],
    },
    {
        "category": "Claims Analytics & Loss Ratios",
        "items": [
            {
                "name": "vw_Top10HighValueClaimants",
                "purpose": "Top 10 highest claim amounts using DENSE_RANK.",
                "ddl": """
CREATE VIEW vw_Top10HighValueClaimants AS
WITH RankedClaims AS (
    SELECT
        CustomerAge,
        PolicyType,
        ClaimAmount,
        DENSE_RANK() OVER (ORDER BY ClaimAmount DESC) AS ClaimRank
    FROM insurance_claims
)
SELECT CustomerAge, PolicyType, ClaimAmount, ClaimRank
FROM RankedClaims
WHERE ClaimRank <= 10;
""",
            },
            {
                "name": "vw_PolicyTypeLossRatio",
                "purpose": "Total and peak claim amounts by policy type (loss intensity).",
                "ddl": """
CREATE VIEW vw_PolicyTypeLossRatio AS
SELECT
    PolicyType AS TypeName,
    ROUND(SUM(ClaimAmount), 2) AS TotalClaimed,
    ROUND(MAX(ClaimAmount), 2) AS PeakClaimValue
FROM insurance_claims
GROUP BY PolicyType;
""",
            },
            {
                "name": "vw_HighHospitalExpenseAnalytics",
                "purpose": "Hospital expense percentiles for Health-related claims.",
                "ddl": """
CREATE VIEW vw_HighHospitalExpenseAnalytics AS
SELECT
    rowid AS ClaimID,
    CustomerAge,
    PolicyType,
    HospitalExpense,
    ROUND(PERCENT_RANK() OVER (ORDER BY HospitalExpense), 4) AS ExpensePercentile
FROM insurance_claims
WHERE HospitalExpense > 0;
""",
            },
        ],
    },
    {
        "category": "Demographic Insights",
        "items": [
            {
                "name": "vw_AgeGroupClaimAnalysis",
                "purpose": "Average and total claim amounts by Youth / Middle-Age / Senior cohort.",
                "ddl": """
CREATE VIEW vw_AgeGroupClaimAnalysis AS
SELECT
    CASE
        WHEN CustomerAge < 30 THEN 'Youth'
        WHEN CustomerAge BETWEEN 30 AND 50 THEN 'Middle-Age'
        ELSE 'Senior'
    END AS AgeGroup,
    ROUND(AVG(ClaimAmount), 2) AS AvgClaimAmount,
    ROUND(SUM(ClaimAmount), 2) AS TotalClaims
FROM insurance_claims
GROUP BY
    CASE
        WHEN CustomerAge < 30 THEN 'Youth'
        WHEN CustomerAge BETWEEN 30 AND 50 THEN 'Middle-Age'
        ELSE 'Senior'
    END;
""",
            },
            {
                "name": "vw_IncomeBracketRiskProfile",
                "purpose": "Claim volume and average payout by income bracket.",
                "ddl": """
CREATE VIEW vw_IncomeBracketRiskProfile AS
SELECT
    CASE
        WHEN AnnualIncome < 500000 THEN 'Low Income'
        WHEN AnnualIncome BETWEEN 500000 AND 1500000 THEN 'Middle Income'
        ELSE 'High Income'
    END AS IncomeBracket,
    COUNT(*) AS TotalClaims,
    ROUND(AVG(ClaimAmount), 2) AS AvgPayout
FROM insurance_claims
GROUP BY
    CASE
        WHEN AnnualIncome < 500000 THEN 'Low Income'
        WHEN AnnualIncome BETWEEN 500000 AND 1500000 THEN 'Middle Income'
        ELSE 'High Income'
    END;
""",
            },
            {
                "name": "vw_SeniorHighValueAnalysis",
                "purpose": "Aggregated claim value for customers aged over 50.",
                "ddl": """
CREATE VIEW vw_SeniorHighValueAnalysis AS
SELECT
    CustomerAge,
    AnnualIncome,
    COUNT(*) AS ClaimCount,
    ROUND(SUM(ClaimAmount), 2) AS LifetimeClaimValue
FROM insurance_claims
WHERE CustomerAge > 50
GROUP BY CustomerAge, AnnualIncome;
""",
            },
        ],
    },
    {
        "category": "Operational Efficiency",
        "items": [
            {
                "name": "vw_ClaimOperationalEfficiency",
                "purpose": "Average claim processing duration by policy type.",
                "ddl": """
CREATE VIEW vw_ClaimOperationalEfficiency AS
SELECT
    PolicyType AS TypeName,
    ROUND(AVG(ClaimDuration), 2) AS AvgDurationDays
FROM insurance_claims
GROUP BY PolicyType;
""",
            },
            {
                "name": "vw_AnnualOperationalThroughput",
                "purpose": "Claims processed per year with total and average processing days.",
                "ddl": """
CREATE VIEW vw_AnnualOperationalThroughput AS
SELECT
    CAST(strftime('%Y', ClaimDate) AS INTEGER) AS ClaimYear,
    COUNT(*) AS ClaimsProcessed,
    SUM(ClaimDuration) AS TotalManDaysSpent,
    ROUND(AVG(ClaimDuration), 2) AS EfficiencyIndex
FROM insurance_claims
GROUP BY strftime('%Y', ClaimDate);
""",
            },
            {
                "name": "vw_PolicyToClaimLag",
                "purpose": "Average days from policy start to claim filing, by policy type.",
                "ddl": """
CREATE VIEW vw_PolicyToClaimLag AS
SELECT
    PolicyType,
    ROUND(AVG(julianday(ClaimDate) - julianday(PolicyStartDate)), 2) AS DaysFromOnboardingToClaim
FROM insurance_claims
GROUP BY PolicyType;
""",
            },
        ],
    },
]


def _create_sqlite_views(connection):
    for group in SQL_VIEWS:
        for view in group["items"]:
            connection.execute(f"DROP VIEW IF EXISTS {view['name']}")
            connection.execute(view["ddl"].strip())


def _show_view(connection, view: dict):
    st.markdown(f"**`{view['name']}`** — {view['purpose']}")
    query_sql = f"SELECT * FROM {view['name']};"
    st.code(view["ddl"].strip() + "\n\n" + query_sql, language="sql")
    try:
        result = run_sql(query_sql, connection)
        st.dataframe(result, use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"View query failed: {e}")


with content_section("Indexes & views (SQL Server design)"):
    st.markdown(
        "Views from `DBModelling_Migration.sql` are recreated in SQLite on the flat "
        "`insurance_claims` table. Each view shows its DDL and a live result table."
    )
    _create_sqlite_views(conn)

    for group in SQL_VIEWS:
        with st.expander(group["category"], expanded=False):
            for view in group["items"]:
                _show_view(conn, view)
                st.markdown("---")
