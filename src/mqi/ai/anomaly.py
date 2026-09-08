from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from mqi.data.synthetic import FEATURES


def fit_anomaly_detector(df: pd.DataFrame, contamination: float = 0.03) -> IsolationForest:
    model = IsolationForest(contamination=contamination, random_state=42, n_estimators=200)
    model.fit(df[FEATURES])
    return model


def anomaly_scores(model: IsolationForest, df: pd.DataFrame) -> np.ndarray:
    return -model.score_samples(df[FEATURES])
