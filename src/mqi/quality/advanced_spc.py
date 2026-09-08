from __future__ import annotations

from dataclasses import dataclass
import numpy as np
from scipy.stats import chi2


@dataclass(frozen=True)
class EWMAResult:
    center: float
    lambda_: float
    lcl: list[float]
    ucl: list[float]
    statistic: list[float]
    signals: list[int]


@dataclass(frozen=True)
class CUSUMResult:
    target: float
    k: float
    h: float
    positive: list[float]
    negative: list[float]
    signals: list[int]


@dataclass(frozen=True)
class HotellingT2Result:
    threshold: float
    t2: list[float]
    signals: list[int]


def ewma_chart(values, baseline_size: int | None = None, lambda_: float = 0.2, L: float = 3.0) -> EWMAResult:
    x = np.asarray(values, dtype=float)
    if x.size < 5:
        raise ValueError("EWMA requires at least five observations")
    if not 0 < lambda_ <= 1:
        raise ValueError("lambda_ must be in (0,1]")
    b = x[: baseline_size or max(5, x.size // 2)]
    mu = float(np.mean(b))
    sigma = float(np.std(b, ddof=1))
    if sigma <= 0:
        raise ValueError("EWMA requires non-zero baseline variation")
    z = np.empty_like(x)
    z[0] = mu
    lcl, ucl = [], []
    signals = []
    for i, value in enumerate(x):
        if i > 0:
            z[i] = lambda_ * value + (1 - lambda_) * z[i - 1]
        width = L * sigma * np.sqrt((lambda_ / (2 - lambda_)) * (1 - (1 - lambda_) ** (2 * (i + 1))))
        lo, hi = mu - width, mu + width
        lcl.append(float(lo)); ucl.append(float(hi))
        if z[i] < lo or z[i] > hi:
            signals.append(i)
    return EWMAResult(mu, lambda_, lcl, ucl, z.astype(float).tolist(), signals)


def cusum_chart(values, baseline_size: int | None = None, k_sigma: float = 0.5, h_sigma: float = 5.0) -> CUSUMResult:
    x = np.asarray(values, dtype=float)
    if x.size < 5:
        raise ValueError("CUSUM requires at least five observations")
    b = x[: baseline_size or max(5, x.size // 2)]
    mu = float(np.mean(b)); sigma = float(np.std(b, ddof=1))
    if sigma <= 0:
        raise ValueError("CUSUM requires non-zero baseline variation")
    k, h = k_sigma * sigma, h_sigma * sigma
    cp = np.zeros_like(x); cm = np.zeros_like(x); signals = []
    for i, value in enumerate(x):
        if i == 0:
            cp[i] = max(0.0, value - mu - k)
            cm[i] = min(0.0, value - mu + k)
        else:
            cp[i] = max(0.0, cp[i-1] + value - mu - k)
            cm[i] = min(0.0, cm[i-1] + value - mu + k)
        if cp[i] > h or cm[i] < -h:
            signals.append(i)
    return CUSUMResult(mu, float(k), float(h), cp.astype(float).tolist(), cm.astype(float).tolist(), signals)


def hotelling_t2(reference, monitoring, alpha: float = 0.99, ridge: float = 1e-6) -> HotellingT2Result:
    ref = np.asarray(reference, dtype=float)
    mon = np.asarray(monitoring, dtype=float)
    if ref.ndim != 2 or mon.ndim != 2 or ref.shape[1] != mon.shape[1]:
        raise ValueError("reference and monitoring must be 2D with matching feature counts")
    if ref.shape[0] <= ref.shape[1]:
        raise ValueError("reference requires more rows than features")
    mu = ref.mean(axis=0)
    cov = np.cov(ref, rowvar=False) + np.eye(ref.shape[1]) * ridge
    inv = np.linalg.pinv(cov)
    delta = mon - mu
    t2 = np.einsum("ij,jk,ik->i", delta, inv, delta)
    threshold = float(chi2.ppf(alpha, df=ref.shape[1]))
    signals = np.where(t2 > threshold)[0].astype(int).tolist()
    return HotellingT2Result(threshold, t2.astype(float).tolist(), signals)
