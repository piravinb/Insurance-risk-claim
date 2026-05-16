"""ML training pipeline ported from ML.py for Streamlit."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import streamlit as st
from imblearn.over_sampling import SMOTE
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeRegressor

from utils.data_loader import get_processed_df

try:
    from xgboost import XGBRegressor
    HAS_XGB = True
except ImportError:
    HAS_XGB = False

APP_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = APP_DIR / "models"
REGRESSION_TARGET = "ClaimAmount"
CLASSIFICATION_TARGET = "FraudRisk"
DATE_COLUMNS = ["PolicyStartDate", "ClaimDate"]
N_SPLITS = 5
RANDOM_STATE = 42


class Preprocessor:
    def __init__(self, numerical_features: list, categorical_features: list):
        self.numerical_features = numerical_features
        self.categorical_features = categorical_features
        self.preprocessor = ColumnTransformer(
            transformers=[
                ("num", Pipeline([("scaler", StandardScaler())]), numerical_features),
                (
                    "cat",
                    Pipeline([("onehot", OneHotEncoder(handle_unknown="ignore"))]),
                    categorical_features,
                ),
            ]
        )

    def fit(self, X: pd.DataFrame):
        self.preprocessor.fit(X)
        return self

    def transform(self, X: pd.DataFrame) -> np.ndarray:
        return self.preprocessor.transform(X)


def _prepare_xy(df: pd.DataFrame):
    cols_drop = DATE_COLUMNS.copy()
    work = df.drop(columns=cols_drop, errors="ignore")
    X_reg = work.drop(columns=[REGRESSION_TARGET, CLASSIFICATION_TARGET], errors="ignore")
    y_reg = work[REGRESSION_TARGET]
    X_clf = work.drop(columns=[CLASSIFICATION_TARGET, REGRESSION_TARGET], errors="ignore")
    y_clf = work[CLASSIFICATION_TARGET]
    return X_reg, y_reg, X_clf, y_clf


def _stratified_folds_regression(y: pd.Series, n_splits: int = N_SPLITS):
    y_binned = pd.cut(y, bins=10, labels=False, include_lowest=True)
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=RANDOM_STATE)
    return list(skf.split(np.zeros(len(y)), y_binned))


def _stratified_folds_classification(y: pd.Series, n_splits: int = N_SPLITS):
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=RANDOM_STATE)
    return list(skf.split(np.zeros(len(y)), y))


def _regression_models():
    models = {
        "RidgeRegression": Ridge(random_state=RANDOM_STATE),
        "DecisionTreeRegressor": DecisionTreeRegressor(random_state=RANDOM_STATE),
    }
    if HAS_XGB:
        models["XGBoostRegressor"] = XGBRegressor(
            random_state=RANDOM_STATE, eval_metric="rmse", verbosity=0
        )
    return models


def _evaluate_regression_cv(X: pd.DataFrame, y: pd.Series, folds):
    models = _regression_models()
    num = X.select_dtypes(include="number").columns.tolist()
    cat = X.select_dtypes(include="object").columns.tolist()
    results = {}

    for name, model_tpl in models.items():
        fold_mae, fold_mse, fold_r2 = [], [], []
        oof_pred = np.zeros(len(y))

        for train_idx, test_idx in folds:
            X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
            y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
            pre = Preprocessor(num, cat)
            X_tr = pre.fit(X_train).transform(X_train)
            X_te = pre.transform(X_test)
            model = deepcopy(model_tpl)
            model.fit(X_tr, y_train)
            pred = model.predict(X_te)
            oof_pred[test_idx] = pred
            fold_mae.append(mean_absolute_error(y_test, pred))
            fold_mse.append(mean_squared_error(y_test, pred))
            fold_r2.append(r2_score(y_test, pred))

        results[name] = {
            "avg_mae": float(np.mean(fold_mae)),
            "avg_mse": float(np.mean(fold_mse)),
            "avg_rmse": float(np.sqrt(np.mean(fold_mse))),
            "avg_r2": float(np.mean(fold_r2)),
            "oof_predictions": oof_pred.tolist(),
            "oof_r2": float(r2_score(y, oof_pred)),
        }

    best = max(results, key=lambda k: results[k]["avg_r2"])
    return best, results


def _evaluate_classification_cv(X: pd.DataFrame, y: pd.Series, folds):
    num = X.select_dtypes(include="number").columns.tolist()
    cat = X.select_dtypes(include="object").columns.tolist()
    smote = SMOTE(random_state=RANDOM_STATE)
    model_tpl = LogisticRegression(
        random_state=RANDOM_STATE, solver="liblinear", class_weight="balanced"
    )

    fold_auc, fold_acc, fold_prec, fold_rec, fold_f1 = [], [], [], [], []
    oof_pred = np.zeros(len(y))
    oof_proba = np.zeros(len(y))
    cms = []

    for train_idx, test_idx in folds:
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
        pre = Preprocessor(num, cat)
        X_tr = pre.fit(X_train).transform(X_train)
        X_te = pre.transform(X_test)
        X_res, y_res = smote.fit_resample(X_tr, y_train)
        model = deepcopy(model_tpl)
        model.fit(X_res, y_res)
        pred = model.predict(X_te)
        proba = model.predict_proba(X_te)[:, 1]
        oof_pred[test_idx] = pred
        oof_proba[test_idx] = proba
        fold_auc.append(roc_auc_score(y_test, proba))
        fold_acc.append(accuracy_score(y_test, pred))
        fold_prec.append(precision_score(y_test, pred, zero_division=0))
        fold_rec.append(recall_score(y_test, pred, zero_division=0))
        fold_f1.append(f1_score(y_test, pred, zero_division=0))
        cms.append(confusion_matrix(y_test, pred, labels=[0, 1]))

    agg_cm = np.sum(cms, axis=0)
    fpr, tpr, _ = roc_curve(y, oof_proba)

    return {
        "avg_auc": float(np.mean(fold_auc)),
        "avg_accuracy": float(np.mean(fold_acc)),
        "avg_precision": float(np.mean(fold_prec)),
        "avg_recall": float(np.mean(fold_rec)),
        "avg_f1": float(np.mean(fold_f1)),
        "confusion_matrix": agg_cm.tolist(),
        "oof_predictions": oof_pred.astype(int).tolist(),
        "oof_proba": oof_proba.tolist(),
        "roc_fpr": fpr.tolist(),
        "roc_tpr": tpr.tolist(),
        "classification_report": classification_report(y, oof_pred.astype(int), output_dict=True),
    }


def train_and_save_models() -> dict:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    df = get_processed_df()
    X_reg, y_reg, X_clf, y_clf = _prepare_xy(df)
    reg_folds = _stratified_folds_regression(y_reg)
    clf_folds = _stratified_folds_classification(y_clf)

    best_reg_name, reg_results = _evaluate_regression_cv(X_reg, y_reg, reg_folds)
    clf_metrics = _evaluate_classification_cv(X_clf, y_clf, clf_folds)

    num_reg = X_reg.select_dtypes(include="number").columns.tolist()
    cat_reg = X_reg.select_dtypes(include="object").columns.tolist()
    num_clf = X_clf.select_dtypes(include="number").columns.tolist()
    cat_clf = X_clf.select_dtypes(include="object").columns.tolist()

    reg_pre = Preprocessor(num_reg, cat_reg)
    X_reg_proc = reg_pre.fit(X_reg).transform(X_reg)
    reg_model = deepcopy(_regression_models()[best_reg_name])
    reg_model.fit(X_reg_proc, y_reg)

    clf_pre = Preprocessor(num_clf, cat_clf)
    X_clf_proc = clf_pre.fit(X_clf).transform(X_clf)
    smote = SMOTE(random_state=RANDOM_STATE)
    X_res, y_res = smote.fit_resample(X_clf_proc, y_clf)
    clf_model = LogisticRegression(
        random_state=RANDOM_STATE, solver="liblinear", class_weight="balanced"
    )
    clf_model.fit(X_res, y_res)

    joblib.dump(reg_model, MODELS_DIR / "regression_model.joblib")
    joblib.dump(reg_pre, MODELS_DIR / "regression_preprocessor.joblib")
    joblib.dump(clf_model, MODELS_DIR / "logistic_model.joblib")
    joblib.dump(clf_pre, MODELS_DIR / "logistic_preprocessor.joblib")

    best_reg = reg_results[best_reg_name]
    metadata = {
        "best_regression_model": best_reg_name,
        "regression_features": X_reg.columns.tolist(),
        "classification_features": X_clf.columns.tolist(),
        "n_splits": N_SPLITS,
        "regression": {
            "avg_mae": best_reg["avg_mae"],
            "avg_mse": best_reg["avg_mse"],
            "avg_rmse": best_reg["avg_rmse"],
            "avg_r2": best_reg["avg_r2"],
            "oof_r2": best_reg["oof_r2"],
            "all_models": {
                k: {kk: vv for kk, vv in v.items() if kk != "oof_predictions"}
                for k, v in reg_results.items()
            },
        },
        "classification": clf_metrics,
        "y_reg": y_reg.tolist(),
        "reg_oof": best_reg["oof_predictions"],
    }
    with open(MODELS_DIR / "regression_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    return metadata


def models_exist() -> bool:
    required = [
        "regression_model.joblib",
        "regression_preprocessor.joblib",
        "logistic_model.joblib",
        "logistic_preprocessor.joblib",
        "regression_metadata.json",
    ]
    return all((MODELS_DIR / f).exists() for f in required)


def load_metadata() -> dict:
    with open(MODELS_DIR / "regression_metadata.json") as f:
        return json.load(f)


def load_models():
    reg_model = joblib.load(MODELS_DIR / "regression_model.joblib")
    reg_pre = joblib.load(MODELS_DIR / "regression_preprocessor.joblib")
    clf_model = joblib.load(MODELS_DIR / "logistic_model.joblib")
    clf_pre = joblib.load(MODELS_DIR / "logistic_preprocessor.joblib")
    metadata = load_metadata()
    return reg_model, reg_pre, clf_model, clf_pre, metadata


def build_input_row(raw: dict) -> pd.DataFrame:
    """Build one-row feature frame for prediction (includes DaysSincePolicyStart)."""
    row = dict(raw)
    if "DaysSincePolicyStart" not in row:
        if "PolicyStartDate" in row and "ClaimDate" in row:
            start = pd.to_datetime(row["PolicyStartDate"])
            claim = pd.to_datetime(row["ClaimDate"])
            row["DaysSincePolicyStart"] = max(0, (claim - start).days)
        else:
            row["DaysSincePolicyStart"] = raw.get("DaysSincePolicyStart", 400)
    drop = DATE_COLUMNS + [REGRESSION_TARGET, CLASSIFICATION_TARGET]
    for c in drop:
        row.pop(c, None)
    return pd.DataFrame([row])


def predict_claim_amount(reg_model, reg_pre, raw: dict) -> float:
    X = build_input_row(raw)
    cols = reg_pre.numerical_features + reg_pre.categorical_features
    X = X[[c for c in cols if c in X.columns]]
    return float(reg_model.predict(reg_pre.transform(X))[0])


def predict_fraud(clf_model, clf_pre, raw: dict) -> tuple[int, float]:
    X = build_input_row(raw)
    cols = clf_pre.numerical_features + clf_pre.categorical_features
    X = X[[c for c in cols if c in X.columns]]
    proba = float(clf_model.predict_proba(clf_pre.transform(X))[0, 1])
    label = 1 if proba >= 0.5 else 0
    return label, proba


@st.cache_resource(show_spinner="Training / loading ML models...")
def train_or_load_models() -> dict:
    if not models_exist():
        return train_and_save_models()
    return load_metadata()


def get_full_model_bundle():
    if not models_exist():
        train_and_save_models()
    return load_models()
