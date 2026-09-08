from __future__ import annotations

from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True)
class SimulationResult:
    mean_defects: float
    p95_defects: float
    mean_cost: float
    p95_cost: float


def simulate_quality(defect_probability: float, volume: int, trials: int = 10000,
                     scrap_cost: float = 85.0, seed: int = 42) -> SimulationResult:
    if not 0 <= defect_probability <= 1:
        raise ValueError("defect_probability must be in [0,1]")
    rng = np.random.default_rng(seed)
    defects = rng.binomial(volume, defect_probability, trials)
    costs = defects * scrap_cost
    return SimulationResult(
        mean_defects=float(defects.mean()),
        p95_defects=float(np.quantile(defects, 0.95)),
        mean_cost=float(costs.mean()),
        p95_cost=float(np.quantile(costs, 0.95)),
    )
