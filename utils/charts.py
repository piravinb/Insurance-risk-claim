"""Reusable Plotly chart builders — Digit color palette."""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

COLORS = {
    "primary": "#111111",
    "accent": "#FFC107",
    "yellow_dark": "#E6AC00",
    "gray": "#4B5563",
    "gray_light": "#E5E7EB",
    "success": "#16A34A",
    "danger": "#DC2626",
    "palette": ["#FFC107", "#111111", "#4B5563", "#E6AC00", "#9CA3AF"],
}

CHART_LAYOUT = dict(
    plot_bgcolor="#FFFFFF",
    paper_bgcolor="#FFFFFF",
    font=dict(family="Inter, sans-serif", color="#111111", size=12),
    title_font=dict(size=15, color="#111111"),
    margin=dict(l=48, r=24, t=56, b=48),
    colorway=COLORS["palette"],
)

MONETARY_COLUMNS = {
    "ClaimAmount", "PremiumAmount", "AnnualIncome",
    "HospitalExpense", "InsuredAmount",
}


def _apply_layout(fig, title: str | None = None, x_col: str | None = None, y_col: str | None = None):
    fig.update_layout(**CHART_LAYOUT)
    if title:
        fig.update_layout(title=dict(text=title, x=0, xanchor="left"))
    fig.update_xaxes(gridcolor="#F3F4F6", linecolor="#E5E7EB")
    fig.update_yaxes(gridcolor="#F3F4F6", linecolor="#E5E7EB")
    if x_col in MONETARY_COLUMNS:
        fig.update_xaxes(tickprefix="₹", tickformat=",")
    if y_col in MONETARY_COLUMNS:
        fig.update_yaxes(tickprefix="₹", tickformat=",")
    return fig


def histogram(df: pd.DataFrame, column: str, title: str, nbins: int = 40):
    fig = px.histogram(
        df, x=column, nbins=nbins, title=title,
        color_discrete_sequence=[COLORS["accent"]],
    )
    fig.update_traces(marker_line_color=COLORS["primary"], marker_line_width=0.5)
    return _apply_layout(fig, title, x_col=column)


def bar_count(df: pd.DataFrame, column: str, title: str):
    counts = df[column].value_counts().reset_index()
    counts.columns = [column, "Count"]
    fig = px.bar(
        counts, x=column, y="Count", title=title, text="Count",
        color_discrete_sequence=COLORS["palette"],
    )
    fig.update_traces(textfont_color="#111111")
    return _apply_layout(fig, title)


def boxplot_by_category(df: pd.DataFrame, y: str, x: str, title: str):
    fig = px.box(df, x=x, y=y, title=title, color=x, color_discrete_sequence=COLORS["palette"])
    return _apply_layout(fig.update_layout(showlegend=False), title, y_col=y)


def correlation_heatmap(df: pd.DataFrame, title: str = "Correlation Heatmap"):
    numeric = df.select_dtypes(include=[np.number])
    corr = numeric.corr()
    fig = px.imshow(
        corr, text_auto=".2f", aspect="auto", title=title,
        color_continuous_scale=[[0, "#FFFFFF"], [0.5, "#FFF8E1"], [1, "#FFC107"]],
        zmin=-1, zmax=1,
    )
    return _apply_layout(fig, title, x_col=x, y_col=y)


def scatter(df: pd.DataFrame, x: str, y: str, title: str, color: str | None = None):
    fig = px.scatter(
        df, x=x, y=y, title=title, color=color,
        opacity=0.55, color_discrete_sequence=COLORS["palette"],
    )
    return _apply_layout(fig, title, x_col=x, y_col=y)


def pie_chart(df: pd.DataFrame, names: str, title: str):
    counts = df[names].value_counts().reset_index()
    counts.columns = [names, "Count"]
    labels = {0: "Low Risk", 1: "High Risk"}
    counts["Label"] = counts[names].map(labels).fillna(counts[names].astype(str))
    fig = px.pie(
        counts, names="Label", values="Count", title=title,
        color_discrete_sequence=["#16A34A", COLORS["accent"]],
    )
    return _apply_layout(fig, title)


def actual_vs_predicted(y_true, y_pred, title: str = "Actual vs Predicted Claim Amount"):
    fig = px.scatter(
        x=y_true, y=y_pred, labels={"x": "Actual", "y": "Predicted"},
        title=title, opacity=0.5, color_discrete_sequence=[COLORS["accent"]],
    )
    mn = min(np.min(y_true), np.min(y_pred))
    mx = max(np.max(y_true), np.max(y_pred))
    fig.add_trace(
        go.Scatter(
            x=[mn, mx], y=[mn, mx], mode="lines", name="Perfect fit",
            line=dict(color=COLORS["primary"], dash="dash", width=2),
        )
    )
    fig.update_xaxes(title_text="Actual (₹)", tickprefix="₹", tickformat=",")
    fig.update_yaxes(title_text="Predicted (₹)", tickprefix="₹", tickformat=",")
    return _apply_layout(fig, title)


def residual_plot(y_true, y_pred, title: str = "Residual Plot"):
    residuals = np.array(y_true) - np.array(y_pred)
    fig = px.scatter(
        x=y_pred, y=residuals, labels={"x": "Predicted", "y": "Residual"},
        title=title, opacity=0.5, color_discrete_sequence=[COLORS["primary"]],
    )
    fig.add_hline(y=0, line_dash="dash", line_color=COLORS["accent"], line_width=2)
    fig.update_xaxes(title_text="Predicted (₹)", tickprefix="₹", tickformat=",")
    fig.update_yaxes(title_text="Residual (₹)", tickprefix="₹", tickformat=",")
    return _apply_layout(fig, title)


def confusion_matrix_heatmap(cm, labels=None, title: str = "Confusion Matrix"):
    if labels is None:
        labels = ["Low Risk (0)", "High Risk (1)"]
    fig = px.imshow(
        cm, text_auto=True, aspect="equal", title=title,
        x=labels, y=labels,
        color_continuous_scale=[[0, "#FFFFFF"], [1, "#FFC107"]],
    )
    return _apply_layout(fig, title)


def roc_curve_plot(fpr, tpr, auc: float, title: str = "ROC Curve"):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=fpr, y=tpr, mode="lines", name=f"ROC (AUC = {auc:.3f})",
        line=dict(color=COLORS["accent"], width=3),
    ))
    fig.add_trace(go.Scatter(
        x=[0, 1], y=[0, 1], mode="lines", name="Random",
        line=dict(color=COLORS["gray"], dash="dash"),
    ))
    fig.update_layout(
        title=title, xaxis_title="False Positive Rate", yaxis_title="True Positive Rate",
    )
    return _apply_layout(fig, title)
