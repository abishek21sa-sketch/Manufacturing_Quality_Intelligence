from __future__ import annotations

from dataclasses import dataclass
import pandas as pd

@dataclass(frozen=True)
class QualityKPI:
    first_pass_yield: float
    defects_per_million: float
    cost_of_poor_quality: float


def quality_kpis(df: pd.DataFrame, scrap_cost: float = 85.0, rework_cost: float = 35.0) -> QualityKPI:
    if "defect" not in df:
        raise ValueError("defect column required")
    defects = int(df["defect"].sum())
    n = len(df)
    fpy = 1 - defects / n if n else 0.0
    # Synthetic demo treats all defects as scrap unless a rework flag is supplied.
    if "rework" in df:
        rework = int(df["rework"].sum())
        copq = (defects - rework) * scrap_cost + rework * rework_cost
    else:
        copq = defects * scrap_cost
    return QualityKPI(float(fpy), float(defects / n * 1_000_000 if n else 0), float(copq))


def defect_pareto(df: pd.DataFrame) -> pd.DataFrame:
    defective = df[df["defect"] == 1]
    counts = defective["defect_type"].value_counts().rename_axis("defect_type").reset_index(name="count")
    if counts.empty:
        counts["cumulative_share"] = []
        return counts
    counts["share"] = counts["count"] / counts["count"].sum()
    counts["cumulative_share"] = counts["share"].cumsum()
    return counts


def identify_bottleneck(station_cycle_times: dict[str, float], available_time: float, demand: int) -> dict:
    if not station_cycle_times or available_time <= 0 or demand <= 0:
        raise ValueError("Valid station cycle times, available_time and demand are required")
    capacities = {s: available_time / ct for s, ct in station_cycle_times.items()}
    bottleneck = min(capacities, key=capacities.get)
    takt = available_time / demand
    return {
        "bottleneck": bottleneck,
        "capacity_units": float(capacities[bottleneck]),
        "takt_time": float(takt),
        "cycle_time": float(station_cycle_times[bottleneck]),
        "demand_feasible": bool(capacities[bottleneck] >= demand),
    }
