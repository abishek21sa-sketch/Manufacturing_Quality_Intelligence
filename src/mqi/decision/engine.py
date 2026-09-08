from __future__ import annotations

from dataclasses import dataclass
import pandas as pd

from mqi.ai.model import coefficient_root_causes
from mqi.decision.root_cause import corrective_actions
from mqi.optimization.inspection import optimize_inspection
from mqi.simulation.monte_carlo import simulate_quality

@dataclass(frozen=True)
class Decision:
    risk: float
    severity: str
    action: str
    inspection_fraction: float
    expected_cost: float
    rationale: list[str]
    root_causes: list[dict]
    corrective_actions: list[dict]


def recommend(model, row: pd.DataFrame, volume: int = 1000) -> Decision:
    risk = float(model.predict_proba(row)[0, 1])
    policy = optimize_inspection(risk, volume)
    sim = simulate_quality(risk, volume, trials=3000)
    roots = coefficient_root_causes(model, row, top_k=4)
    checks = corrective_actions(roots)
    if risk >= 0.30:
        severity, action = "critical", "Hold affected lot; initiate containment and process parameter review"
    elif risk >= 0.15:
        severity, action = "high", "Increase inspection and investigate leading process contributors"
    elif risk >= 0.075:
        severity, action = "medium", "Apply targeted sampling and monitor SPC signals"
    else:
        severity, action = "low", "Continue standard control plan"
    rationale = [
        f"Predicted defect probability {risk:.3f}",
        f"Cost-minimizing inspection fraction {policy.sample_fraction:.2f}",
        f"Monte Carlo mean defects per {volume} units {sim.mean_defects:.1f}",
        f"Monte Carlo P95 quality cost ${sim.p95_cost:,.0f}",
    ]
    return Decision(risk, severity, action, policy.sample_fraction, policy.expected_total_cost, rationale, roots, checks)
