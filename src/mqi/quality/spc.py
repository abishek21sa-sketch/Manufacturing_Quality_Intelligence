from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
import numpy as np
import pandas as pd
from scipy.stats import norm

@dataclass(frozen=True)
class ControlLimits:
    center: float
    lcl: float
    ucl: float

@dataclass(frozen=True)
class Capability:
    cp: float
    cpk: float
    mean: float
    sigma: float


def individuals_chart(values, sigma: float | None = None, k: float = 3.0) -> ControlLimits:
    x = np.asarray(values, dtype=float)
    if x.size < 2:
        raise ValueError("At least two observations are required")
    center = float(np.mean(x))
    if sigma is None:
        mr = np.abs(np.diff(x))
        sigma = float(np.mean(mr) / 1.128) if mr.size else float(np.std(x, ddof=1))
    return ControlLimits(center, center - k * sigma, center + k * sigma)


def p_chart(defects, subgroup_size: int, k: float = 3.0) -> ControlLimits:
    d = np.asarray(defects, dtype=float)
    pbar = float(np.mean(d))
    se = sqrt(max(pbar * (1 - pbar) / subgroup_size, 0.0))
    return ControlLimits(pbar, max(0.0, pbar - k * se), min(1.0, pbar + k * se))


def capability(values, lsl: float, usl: float) -> Capability:
    x = np.asarray(values, dtype=float)
    if not lsl < usl:
        raise ValueError("LSL must be below USL")
    mu = float(np.mean(x))
    sigma = float(np.std(x, ddof=1))
    if sigma <= 0:
        raise ValueError("Capability requires non-zero variation")
    cp = (usl - lsl) / (6 * sigma)
    cpk = min((usl - mu) / (3 * sigma), (mu - lsl) / (3 * sigma))
    return Capability(float(cp), float(cpk), mu, sigma)


def detect_rule1(values, limits: ControlLimits) -> list[int]:
    x = np.asarray(values, dtype=float)
    return np.where((x < limits.lcl) | (x > limits.ucl))[0].astype(int).tolist()


def acceptance_sample_size(aql: float, alpha: float = 0.05, c: int = 0) -> int:
    """Smallest n for a zero/low-acceptance plan with P(accept|AQL) >= 1-alpha.

    For c=0, acceptance probability is (1-aql)^n. This utility intentionally
    supports the conservative zero-acceptance plan used in the demo.
    """
    if not (0 < aql < 1) or not (0 < alpha < 1) or c != 0:
        raise ValueError("Current implementation supports 0<aql<1, 0<alpha<1, c=0")
    # For a producer-friendly AQL criterion, cap n at the largest n satisfying the condition.
    n = int(np.floor(np.log(1 - alpha) / np.log(1 - aql)))
    return max(n, 1)


def process_sigma_level(cpk: float, shift: float = 1.5) -> float:
    return float(3.0 * cpk + shift)
