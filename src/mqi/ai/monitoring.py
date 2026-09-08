from __future__ import annotations

from dataclasses import dataclass
import numpy as np
import pandas as pd


@dataclass(frozen=True)
class DriftFeature:
    feature: str
    psi: float
    status: str


@dataclass(frozen=True)
class DriftReport:
    overall_status: str
    max_psi: float
    features: list[dict]


def population_stability_index(reference, current, bins: int = 10) -> float:
    ref = np.asarray(reference, dtype=float)
    cur = np.asarray(current, dtype=float)
    ref = ref[np.isfinite(ref)]; cur = cur[np.isfinite(cur)]
    if ref.size < bins or cur.size < bins:
        raise ValueError("PSI requires sufficient finite observations")
    edges = np.unique(np.quantile(ref, np.linspace(0, 1, bins + 1)))
    if edges.size < 3:
        return 0.0
    edges[0] = -np.inf; edges[-1] = np.inf
    r = np.histogram(ref, bins=edges)[0] / ref.size
    c = np.histogram(cur, bins=edges)[0] / cur.size
    eps = 1e-6
    return float(np.sum((c - r) * np.log((c + eps) / (r + eps))))


def drift_report(reference: pd.DataFrame, current: pd.DataFrame, features: list[str]) -> DriftReport:
    rows = []
    for feature in features:
        psi = population_stability_index(reference[feature], current[feature])
        status = "stable" if psi < 0.10 else "watch" if psi < 0.25 else "drift"
        rows.append(DriftFeature(feature, psi, status).__dict__)
    maximum = max((x["psi"] for x in rows), default=0.0)
    overall = "stable" if maximum < 0.10 else "watch" if maximum < 0.25 else "drift"
    return DriftReport(overall, float(maximum), rows)
