import numpy as np
import pandas as pd
import streamlit as st

from utils.app_style import content_section, format_inr, insight, page_header, spacer
from utils.charts import actual_vs_predicted, residual_plot
from utils.model_trainer import train_or_load_models

page_header(
    "Claim Amount Prediction",
    "Best regression model selected via 5-fold stratified cross-validation.",
    tag="Machine Learning",
)

with st.spinner("Loading model results..."):
    meta = train_or_load_models()

reg = meta["regression"]
best_name = meta["best_regression_model"]
features = meta["regression_features"]

with content_section("How it works"):
    st.markdown(
        """
        **Regression** estimates payout (`ClaimAmount`) from customer and policy features.
        We compared **Ridge**, **Decision Tree**, and **XGBoost** with **5-fold stratified CV**
        (target binned into deciles), matching the capstone `ML.py` pipeline.
        """
    )
    st.success(f"**Selected model:** {best_name} (highest average CV R²)")
    st.code(", ".join(features))
    insight(
        f"**{meta['n_splits']}-fold stratified CV** — metrics are averaged across folds. "
        "Out-of-fold (OOF) predictions power the charts below."
    )

with content_section("Performance metrics"):
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("MAE (CV avg)", format_inr(reg["avg_mae"]))
    c2.metric("MSE (CV avg)", format_inr(reg["avg_mse"]))
    c3.metric("RMSE (CV avg)", format_inr(reg["avg_rmse"]))
    c4.metric("R² (CV avg)", f"{reg['avg_r2']:.3f}")
    c5.metric("R² (OOF)", f"{reg['oof_r2']:.3f}")

y_true = np.array(meta["y_reg"])
y_oof = np.array(meta["reg_oof"])

with content_section("Diagnostics"):
    st.plotly_chart(actual_vs_predicted(y_true, y_oof), use_container_width=True)
    spacer("sm")
    st.plotly_chart(residual_plot(y_true, y_oof), use_container_width=True)

    gap = reg["avg_r2"] - reg["oof_r2"]
    if gap > 0.08:
        insight("**Possible overfitting** — CV performance may exceed OOF generalization.")
    elif reg["oof_r2"] < 0.5:
        insight("**Weak fit** — OOF R² is low; consider more features or another algorithm.")
    else:
        insight("**Good fit** — OOF R² is strong and aligned with CV average for this portfolio.")

with content_section("All candidates"):
    rows = [
        {
            "Model": name,
            "MAE (₹)": format_inr(m["avg_mae"]),
            "RMSE (₹)": format_inr(m["avg_rmse"]),
            "R²": m["avg_r2"],
        }
        for name, m in reg["all_models"].items()
    ]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
