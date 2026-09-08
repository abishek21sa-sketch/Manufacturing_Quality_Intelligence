from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, balanced_accuracy_score, brier_score_loss, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from mqi.data.synthetic import FEATURES

@dataclass(frozen=True)
class ModelMetrics:
    roc_auc: float
    average_precision: float
    balanced_accuracy: float
    brier_score: float
    decision_threshold: float
    holdout_defect_rate: float
    mean_predicted_probability: float


def build_model() -> Pipeline:
    prep = ColumnTransformer([
        ("numeric", Pipeline([("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())]), FEATURES)
    ])
    # Unweighted logistic regression is used as the probability baseline because the
    # predicted probability feeds simulation and optimization. Class weighting can
    # materially distort probability calibration even when ranking remains useful.
    clf = LogisticRegression(max_iter=2000, random_state=42)
    return Pipeline([("prep", prep), ("model", clf)])


def _select_threshold(y: pd.Series, p: np.ndarray) -> float:
    # Select on training-tail-like predictions would be ideal in production. For this
    # reproducible baseline, choose from a small governed policy grid based on holdout
    # balanced accuracy and persist the chosen threshold as evidence.
    candidates = np.array([0.05, 0.075, 0.10, 0.125, 0.15, 0.20, 0.25, 0.30])
    scores = [balanced_accuracy_score(y, p >= t) for t in candidates]
    return float(candidates[int(np.argmax(scores))])


def train_temporal(df: pd.DataFrame) -> tuple[Pipeline, ModelMetrics, pd.DataFrame]:
    """Temporal train/validation/test split with threshold selection isolated from test.

    First 70% trains the probability model, next 10% governs the decision threshold,
    and final 20% remains untouched until final evaluation.
    """
    ordered = df.sort_values("event_time").reset_index(drop=True)
    train_cut = int(len(ordered) * 0.70)
    val_cut = int(len(ordered) * 0.80)
    train = ordered.iloc[:train_cut]
    validation = ordered.iloc[train_cut:val_cut]
    test = ordered.iloc[val_cut:]
    model = build_model().fit(train[FEATURES], train["defect"])
    p_val = model.predict_proba(validation[FEATURES])[:, 1]
    threshold = _select_threshold(validation["defect"], p_val)
    p = model.predict_proba(test[FEATURES])[:, 1]
    pred = (p >= threshold).astype(int)
    metrics = ModelMetrics(
        roc_auc=float(roc_auc_score(test["defect"], p)),
        average_precision=float(average_precision_score(test["defect"], p)),
        balanced_accuracy=float(balanced_accuracy_score(test["defect"], pred)),
        brier_score=float(brier_score_loss(test["defect"], p)),
        decision_threshold=threshold,
        holdout_defect_rate=float(test["defect"].mean()),
        mean_predicted_probability=float(p.mean()),
    )
    scored = test[["event_time", "part_id", "defect"]].copy()
    scored["defect_probability"] = p
    scored["risk_flag"] = (p >= threshold).astype(int)
    return model, metrics, scored


def save_model(model: Pipeline, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, path)


def load_model(path: Path) -> Pipeline:
    return joblib.load(path)


def coefficient_root_causes(model: Pipeline, row: pd.DataFrame, top_k: int = 5) -> list[dict]:
    transformed = model.named_steps["prep"].transform(row[FEATURES])
    coef = model.named_steps["model"].coef_[0]
    contrib = np.asarray(transformed)[0] * coef
    idx = np.argsort(np.abs(contrib))[::-1][:top_k]
    return [{"feature": FEATURES[i], "signed_contribution": float(contrib[i])} for i in idx]
