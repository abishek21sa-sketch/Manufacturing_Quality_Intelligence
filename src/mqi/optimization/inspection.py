from __future__ import annotations

from dataclasses import dataclass
import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp


@dataclass(frozen=True)
class InspectionPolicy:
    sample_fraction: float
    expected_total_cost: float
    expected_escape_cost: float
    inspection_cost: float
    detection_probability: float


def optimize_inspection(defect_probability: float, volume: int, inspection_cost_per_unit: float = 1.2,
                        escape_cost_per_defect: float = 180.0,
                        detection_effectiveness: float = 0.95,
                        candidate_fractions=(0.0, 0.1, 0.25, 0.5, 1.0),
                        max_inspections: int | None = None) -> InspectionPolicy:
    if not 0 <= defect_probability <= 1:
        raise ValueError("defect_probability must be in [0,1]")
    if volume <= 0:
        raise ValueError("volume must be positive")
    feasible = []
    for f in candidate_fractions:
        if not 0 <= f <= 1:
            raise ValueError("candidate fractions must be in [0,1]")
        inspected = volume * f
        if max_inspections is not None and inspected > max_inspections:
            continue
        detection = f * detection_effectiveness
        insp_cost = inspected * inspection_cost_per_unit
        escape_cost = volume * defect_probability * (1 - detection) * escape_cost_per_defect
        feasible.append(InspectionPolicy(float(f), float(insp_cost + escape_cost), float(escape_cost), float(insp_cost), float(detection)))
    if not feasible:
        raise ValueError("No feasible inspection policy")
    return min(feasible, key=lambda p: p.expected_total_cost)


@dataclass(frozen=True)
class AllocationResult:
    fractions: dict[str, float]
    expected_total_cost: float
    inspected_units: float
    capacity: int
    solver: str
    status: str
    optimality_gap: float | None


def optimize_multi_station(station_risks: dict[str, float], volumes: dict[str, int], capacity: int,
                           fractions=(0.0, 0.25, 0.5, 1.0), inspection_cost=1.0,
                           escape_cost=200.0, effectiveness=0.95) -> AllocationResult:
    """MILP inspection allocation with one discrete sampling policy per station.

    Binary y[s,f] selects exactly one inspection fraction for each station. The objective
    minimizes inspection cost plus expected escaped-defect cost subject to total inspection
    capacity. SciPy/HiGHS is used so the public repository remains reproducible without a
    commercial license; the formulation is solver-portable to Gurobi.
    """
    stations = list(station_risks)
    if not stations or set(stations) != set(volumes):
        raise ValueError("station_risks and volumes must contain the same non-empty stations")
    if capacity < 0:
        raise ValueError("capacity must be non-negative")
    if any(not 0 <= station_risks[s] <= 1 for s in stations):
        raise ValueError("station risks must be in [0,1]")
    if any(volumes[s] <= 0 for s in stations):
        raise ValueError("volumes must be positive")
    fractions = tuple(float(f) for f in fractions)
    if not fractions or any(not 0 <= f <= 1 for f in fractions):
        raise ValueError("fractions must be non-empty and in [0,1]")

    n_s, n_f = len(stations), len(fractions)
    n = n_s * n_f
    c = np.zeros(n)
    inspected = np.zeros(n)
    for i, s in enumerate(stations):
        for j, f in enumerate(fractions):
            k = i * n_f + j
            inspected[k] = volumes[s] * f
            c[k] = (volumes[s] * f * inspection_cost +
                    volumes[s] * station_risks[s] * (1 - f * effectiveness) * escape_cost)

    # Exactly one fraction per station.
    Aeq = np.zeros((n_s, n))
    for i in range(n_s):
        Aeq[i, i*n_f:(i+1)*n_f] = 1.0
    constraints = [LinearConstraint(Aeq, np.ones(n_s), np.ones(n_s)),
                   LinearConstraint(inspected.reshape(1, -1), -np.inf, np.array([capacity], dtype=float))]
    result = milp(c=c, integrality=np.ones(n), bounds=Bounds(np.zeros(n), np.ones(n)),
                  constraints=constraints, options={"time_limit": 30.0, "mip_rel_gap": 0.0})
    status_map = {0: "OPTIMAL", 1: "LIMIT_REACHED", 2: "INFEASIBLE", 3: "UNBOUNDED", 4: "SOLVER_ERROR"}
    status = status_map.get(result.status, "UNKNOWN")
    if result.x is None or status not in {"OPTIMAL", "LIMIT_REACHED"}:
        raise ValueError(f"Inspection allocation failed with solver status {status}: {result.message}")
    chosen = {}
    for i, s in enumerate(stations):
        block = result.x[i*n_f:(i+1)*n_f]
        chosen[s] = fractions[int(np.argmax(block))]
    used = float(sum(volumes[s] * chosen[s] for s in stations))
    gap = getattr(result, "mip_gap", None)
    return AllocationResult(chosen, float(result.fun), used, capacity, "SciPy/HiGHS MILP", status,
                            None if gap is None else float(gap))
