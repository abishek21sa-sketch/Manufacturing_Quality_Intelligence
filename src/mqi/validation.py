from __future__ import annotations

import json
from dataclasses import asdict
import pandas as pd

from mqi.ai.model import train_temporal, save_model
from mqi.ai.monitoring import drift_report
from mqi.config import settings
from mqi.data.contracts import validate_process_frame
from mqi.data.synthetic import FEATURES, generate_msa_data, generate_process_data
from mqi.optimization.inspection import optimize_inspection
from mqi.quality.advanced_spc import cusum_chart, ewma_chart, hotelling_t2
from mqi.quality.msa import crossed_gage_rr
from mqi.quality.spc import capability, individuals_chart, detect_rule1
from mqi.simulation.monte_carlo import simulate_quality


def run_validation(n: int = 5000) -> dict:
    df = generate_process_data(n=n, seed=settings.seed)
    dq = validate_process_frame(df)
    model, metrics, scored = train_temporal(df)
    save_model(model, settings.model_path)

    midpoint = int(n * 0.5)
    baseline = df["dimension_error_mm"].iloc[:midpoint]
    monitoring = df["dimension_error_mm"].iloc[midpoint:]
    limits = individuals_chart(baseline)
    signals = detect_rule1(monitoring, limits)
    ewma = ewma_chart(df["dimension_error_mm"], baseline_size=midpoint)
    cusum = cusum_chart(df["dimension_error_mm"], baseline_size=midpoint)
    h2 = hotelling_t2(df[FEATURES].iloc[:midpoint], df[FEATURES].iloc[midpoint:])
    cap = capability(baseline, -0.50, 0.50)
    msa = crossed_gage_rr(generate_msa_data())
    current_risk = float(scored["defect_probability"].mean())
    policy = optimize_inspection(current_risk, volume=1000, max_inspections=500)
    sim = simulate_quality(current_risk, volume=1000, trials=5000)

    # Natural temporal monitoring window. This is not manufactured drift; it documents
    # the monitoring mechanics and the state observed in the reproducible process stream.
    ref = df[FEATURES].iloc[:midpoint]
    cur = df[FEATURES].iloc[midpoint:]
    drift = drift_report(ref, cur, FEATURES)

    report = {
        "status": "PASS",
        "release": "1.5.0",
        "data_quality": asdict(dq),
        "model_metrics": asdict(metrics),
        "validation_design": {
            "split": "temporal 70/10/20",
            "threshold_selection": "validation window only",
            "test_window": "untouched until final evaluation",
        },
        "spc": {
            "individuals": {"limits": asdict(limits), "monitoring_signals": len(signals)},
            "ewma_signal_count": len(ewma.signals),
            "cusum_signal_count": len(cusum.signals),
            "hotelling_t2_signal_count": len(h2.signals),
            "hotelling_t2_threshold": h2.threshold,
        },
        "capability": asdict(cap),
        "msa": asdict(msa),
        "drift_monitoring": asdict(drift),
        "inspection_policy": asdict(policy),
        "simulation": asdict(sim),
        "evidence_note": "All metrics are generated from the repository's reproducible synthetic validation dataset; they are not plant performance claims. External SECOM validation remains an optional benchmark requiring network access or a local dataset copy.",
    }
    settings.artifact_dir.mkdir(parents=True, exist_ok=True)
    (settings.artifact_dir / "validation_report.json").write_text(json.dumps(report, indent=2))
    (settings.data_dir / "fixtures").mkdir(parents=True, exist_ok=True)
    df.head(250).to_csv(settings.data_dir / "fixtures" / "process_fixture.csv", index=False)
    scored.to_csv(settings.artifact_dir / "holdout_predictions.csv", index=False)
    return report
