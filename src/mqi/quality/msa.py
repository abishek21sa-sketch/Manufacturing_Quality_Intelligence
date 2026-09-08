from __future__ import annotations

from dataclasses import dataclass
import numpy as np
import pandas as pd

@dataclass(frozen=True)
class GageRRResult:
    repeatability_sd: float
    reproducibility_sd: float
    gage_rr_sd: float
    part_to_part_sd: float
    percent_study_variation: float


def crossed_gage_rr(df: pd.DataFrame, measurement="measurement", part="part", operator="operator") -> GageRRResult:
    """Practical crossed Gage R&R variance-component approximation for balanced studies."""
    required = {measurement, part, operator}
    if not required.issubset(df.columns):
        raise ValueError(f"Missing columns: {sorted(required - set(df.columns))}")
    cell = df.groupby([part, operator])[measurement]
    repeat_var = float(cell.var(ddof=1).mean())
    repeat_sd = np.sqrt(max(repeat_var, 0))

    op_means = df.groupby(operator)[measurement].mean()
    reproducibility_sd = float(op_means.std(ddof=1)) if len(op_means) > 1 else 0.0

    part_means = df.groupby(part)[measurement].mean()
    part_sd = float(part_means.std(ddof=1)) if len(part_means) > 1 else 0.0
    grr = float(np.sqrt(repeat_sd**2 + reproducibility_sd**2))
    total = float(np.sqrt(grr**2 + part_sd**2))
    pct = 100 * grr / total if total > 0 else 0.0
    return GageRRResult(float(repeat_sd), reproducibility_sd, grr, part_sd, float(pct))
