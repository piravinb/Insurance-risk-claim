import numpy as np
import pandas as pd
import streamlit as st

from utils.app_style import content_section, insight, page_header, spacer
from utils.charts import confusion_matrix_heatmap, roc_curve_plot
from utils.model_trainer import train_or_load_models

page_header(
    "Fraud Risk Detection",
    "Logistic regression with SMOTE — ClaimAmount excluded to prevent leakage.",
    tag="Machine Learning",
)

with st.spinner("Loading classification results..."):
    meta = train_or_load_models()

clf = meta["classification"]
features = meta["classification_features"]

with content_section("Model overview"):
    st.markdown(
        """
        **Logistic regression** classifies claims as **high fraud risk** (1) or **low risk** (0).
        Training applies **SMOTE** on each CV fold and `class_weight='balanced'`.
        """
    )
    st.code(", ".join(features))
    st.caption("ClaimAmount is intentionally omitted from fraud features.")

with content_section("Performance metrics"):
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("ROC AUC (CV avg)", f"{clf['avg_auc']:.3f}")
    c2.metric("Accuracy", f"{clf['avg_accuracy']:.3f}")
    c3.metric("Precision", f"{clf['avg_precision']:.3f}")
    c4.metric("Recall", f"{clf['avg_recall']:.3f}")

with content_section("Confusion matrix (OOF)"):
    cm = np.array(clf["confusion_matrix"])
    st.plotly_chart(
        confusion_matrix_heatmap(cm, labels=["Predicted Low", "Predicted High"]),
        use_container_width=True,
    )
    insight(
        "**Top-left:** true negatives (cleared). **Bottom-right:** true positives (fraud caught). "
        "**Top-right:** false positives (extra review). **Bottom-left:** false negatives (missed fraud)."
    )

with content_section("Classification report"):
    report = clf["classification_report"]
    rows = []
    for label in ["0", "1"]:
        if label in report:
            rows.append({
                "Class": "Low Risk" if label == "0" else "High Risk",
                "Precision": round(report[label]["precision"], 3),
                "Recall": round(report[label]["recall"], 3),
                "F1-Score": round(report[label]["f1-score"], 3),
                "Support": int(report[label]["support"]),
            })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

with content_section("ROC curve"):
    st.plotly_chart(
        roc_curve_plot(clf["roc_fpr"], clf["roc_tpr"], clf["avg_auc"]),
        use_container_width=True,
    )
    auc = clf["avg_auc"]
    if auc >= 0.85:
        tier = "**Good** — strong separation; suitable for triage with human review."
    elif auc >= 0.70:
        tier = "**Average** — useful ranking; tune thresholds and keep investigators in the loop."
    else:
        tier = "**Poor** — limited discrimination; improve features or modeling before automation."
    insight(f"**Assessment:** {tier} Recall ({clf['avg_recall']:.2f}) is critical for fraud — missed claims cost more than extra reviews.")
