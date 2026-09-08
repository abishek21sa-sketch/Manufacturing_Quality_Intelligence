from __future__ import annotations

import numpy as np
import pandas as pd

FEATURES = [
    "temperature_c", "pressure_bar", "speed_mpm", "vibration_mm_s",
    "tool_wear_pct", "material_hardness", "humidity_pct", "operator_experience_y"
]


def generate_process_data(n: int = 5000, seed: int = 42) -> pd.DataFrame:
    """Create a reproducible machining/coating-style quality process stream.

    The synthetic generator is intentionally structured: quality risk increases with
    excessive temperature, pressure drift, tool wear, vibration, and interactions.
    It supports reproducible end-to-end validation without pretending to be plant data.
    """
    rng = np.random.default_rng(seed)
    t = np.arange(n)
    temperature = rng.normal(180, 5.5, n) + 0.0025 * t
    pressure = rng.normal(8.0, 0.45, n) + np.where(t > n * 0.70, 0.65, 0)
    speed = rng.normal(42, 3.5, n)
    vibration = np.clip(rng.normal(2.1, 0.55, n) + 0.018 * np.maximum(0, temperature - 184), 0.2, None)
    tool_wear = np.clip((t % 700) / 7 + rng.normal(0, 3.0, n), 0, 100)
    hardness = rng.normal(62, 3.8, n)
    humidity = np.clip(rng.normal(48, 9, n), 15, 85)
    operator_exp = np.clip(rng.gamma(3, 1.5, n), 0.2, 20)

    dimensional_error = (
        0.014 * (temperature - 180)
        + 0.08 * (pressure - 8)
        + 0.005 * (speed - 42)
        + 0.025 * (vibration - 2.1)
        + 0.0018 * tool_wear
        + rng.normal(0, 0.12, n)
    )
    surface_roughness = (
        1.45 + 0.035 * vibration + 0.012 * tool_wear + 0.008 * np.maximum(0, hardness - 64)
        + rng.normal(0, 0.17, n)
    )

    logit = (
        -5.2
        + 0.11 * np.maximum(0, temperature - 184)
        + 0.65 * np.maximum(0, pressure - 8.45)
        + 0.027 * tool_wear
        + 0.48 * np.maximum(0, vibration - 2.6)
        + 1.5 * np.abs(dimensional_error)
        + 0.35 * np.maximum(0, surface_roughness - 2.2)
        - 0.03 * operator_exp
    )
    p_defect = 1 / (1 + np.exp(-logit))
    defect = rng.binomial(1, np.clip(p_defect, 0.001, 0.95))

    defect_type = np.where(
        defect == 0, "none",
        np.where(np.abs(dimensional_error) > 0.32, "dimension",
                 np.where(surface_roughness > 2.35, "surface", "process"))
    )
    line = np.where(t % 2 == 0, "L1", "L2")
    shift = np.array(["A", "B", "C"])[(t // 250) % 3]

    return pd.DataFrame({
        "event_time": pd.date_range("2026-01-01", periods=n, freq="min"),
        "part_id": [f"P{i:07d}" for i in range(n)],
        "line": line,
        "shift": shift,
        "temperature_c": temperature,
        "pressure_bar": pressure,
        "speed_mpm": speed,
        "vibration_mm_s": vibration,
        "tool_wear_pct": tool_wear,
        "material_hardness": hardness,
        "humidity_pct": humidity,
        "operator_experience_y": operator_exp,
        "dimension_error_mm": dimensional_error,
        "surface_roughness_ra": surface_roughness,
        "defect": defect,
        "defect_type": defect_type,
    })


def generate_msa_data(parts: int = 10, operators: int = 3, repeats: int = 3, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    true_values = rng.normal(50.0, 0.8, parts)
    rows = []
    for p in range(parts):
        for o in range(operators):
            operator_bias = rng.normal(0, 0.025)
            for r in range(repeats):
                measured = true_values[p] + operator_bias + rng.normal(0, 0.045)
                rows.append({"part": f"part_{p+1}", "operator": f"op_{o+1}", "repeat": r+1, "measurement": measured})
    return pd.DataFrame(rows)
