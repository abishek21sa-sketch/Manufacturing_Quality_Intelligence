from __future__ import annotations

import itertools
import numpy as np
import pandas as pd


def full_factorial_two_level(factors: dict[str, tuple[float, float]]) -> pd.DataFrame:
    names = list(factors)
    rows = []
    for coded in itertools.product([-1, 1], repeat=len(names)):
        row = {}
        for name, level in zip(names, coded):
            low, high = factors[name]
            row[name] = low if level == -1 else high
            row[f"{name}_coded"] = level
        rows.append(row)
    return pd.DataFrame(rows)


def estimate_main_effects(df: pd.DataFrame, response: str, coded_factors: list[str]) -> dict[str, float]:
    y = df[response].to_numpy(float)
    effects = {}
    for factor in coded_factors:
        x = df[factor].to_numpy(float)
        effects[factor] = float(np.mean(y[x > 0]) - np.mean(y[x < 0]))
    return effects
