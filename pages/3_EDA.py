import plotly.express as px
import streamlit as st

from utils.app_style import content_section, insight, page_header, spacer
from utils.charts import (
    COLORS,
    bar_count,
    boxplot_by_category,
    correlation_heatmap,
    histogram,
    pie_chart,
    scatter,
)
from utils.data_loader import load_dataset

page_header(
    "Exploratory Data Analysis",
    "Interactive charts with plain-language insights across the portfolio.",
    tag="Analytics",
)

with st.spinner("Loading data..."):
    df = load_dataset()

with content_section("Claim & premium distributions"):
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(histogram(df, "ClaimAmount", "Claim Amount Distribution"), use_container_width=True)
        insight("Claim amounts are **right-skewed** — most payouts are moderate with a long tail of high-severity claims.")
    with c2:
        st.plotly_chart(histogram(df, "PremiumAmount", "Premium Amount Distribution"), use_container_width=True)
        insight("Premiums vary by age, income, and policy loading — reflecting **risk-based pricing**.")

spacer("sm")

with content_section("Policy mix & claim severity"):
    st.plotly_chart(bar_count(df, "PolicyType", "Policy Type Distribution"), use_container_width=True)
    insight("**Health** and **Vehicle** dominate (~35% each), aligned with typical market share.")
    spacer("sm")
    st.plotly_chart(
        boxplot_by_category(df, "ClaimAmount", "PolicyType", "Claim Amount by Policy Type"),
        use_container_width=True,
    )
    insight("**Life** and **Health** show higher medians and wider spreads; **Travel** claims tend to be smaller.")

spacer("sm")

with content_section("Correlations"):
    st.plotly_chart(correlation_heatmap(df), use_container_width=True)
    insight("Insured amount, premium, income, and hospital expense correlate with claim amount — strong regression predictors.")

with content_section("Demographics & fraud"):
    c1, c2 = st.columns([1.2, 1])
    with c1:
        st.plotly_chart(histogram(df, "CustomerAge", "Customer Age Distribution", nbins=30), use_container_width=True)
        insight("Ages cluster around **35–50**, the core insurance-buying demographic.")
    with c2:
        st.plotly_chart(pie_chart(df, "FraudRisk", "Fraud Risk"), use_container_width=True)
        st.metric("Fraud rate", f"{100 * df['FraudRisk'].mean():.1f}%")
        insight("~25% flagged high-risk — intentional class balance for the fraud model.")

spacer("sm")

with content_section("Income vs claims"):
    sample = df.sample(min(800, len(df)), random_state=42)
    st.plotly_chart(
        scatter(sample, "AnnualIncome", "ClaimAmount", "Annual Income vs Claim Amount", color="PolicyType"),
        use_container_width=True,
    )
    insight("Higher-income customers file larger claims; many points approach the **insured-amount ceiling**.")

with content_section("Previous claims frequency"):
    prev = df["PreviousClaims"].value_counts().sort_index().reset_index()
    prev.columns = ["PreviousClaims", "Count"]
    fig = px.bar(prev, x="PreviousClaims", y="Count", title="Previous Claims Distribution",
                 color_discrete_sequence=[COLORS["accent"]])
    fig.update_layout(plot_bgcolor="white", paper_bgcolor="white")
    st.plotly_chart(fig, use_container_width=True)
    insight("Most customers have **0–2** prior claims; counts of **5+** are rare but linked to fraud in the data rules.")
