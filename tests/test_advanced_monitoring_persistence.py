from pathlib import Path

import numpy as np
import pandas as pd

from mqi.ai.monitoring import drift_report, population_stability_index
from mqi.data.synthetic import FEATURES, generate_process_data
from mqi.persistence import DecisionStore
from mqi.quality.advanced_spc import cusum_chart, ewma_chart, hotelling_t2


def test_ewma_and_cusum_detect_shift():
    rng = np.random.default_rng(4)
    values = np.r_[rng.normal(0, 1, 150), rng.normal(2.5, 1, 80)]
    ewma = ewma_chart(values, baseline_size=120)
    cusum = cusum_chart(values, baseline_size=120)
    assert any(i >= 150 for i in ewma.signals)
    assert any(i >= 150 for i in cusum.signals)


def test_hotelling_t2_detects_multivariate_shift():
    rng = np.random.default_rng(9)
    ref = rng.normal(0, 1, size=(300, 3))
    mon = rng.normal(2.0, 1, size=(80, 3))
    out = hotelling_t2(ref, mon)
    assert len(out.signals) > 30
    assert out.threshold > 0


def test_psi_and_drift_report():
    rng = np.random.default_rng(2)
    ref = rng.normal(0, 1, 1000)
    shifted = rng.normal(1.5, 1, 1000)
    assert population_stability_index(ref, shifted) > 0.25
    df = generate_process_data(800, seed=3)
    reference = df[FEATURES].iloc[:400].copy()
    current = reference.copy()
    current["temperature_c"] += 8
    report = drift_report(reference, current, FEATURES)
    assert report.overall_status in {"watch", "drift"}
    assert max(x["psi"] for x in report.features) > 0.1


def test_decision_store_roundtrip(tmp_path: Path):
    store = DecisionStore(tmp_path / "decisions.sqlite3")
    response = {"risk": 0.21, "severity": "high", "action": "inspect"}
    decision_id = store.record({"temperature_c": 190}, response)
    assert decision_id == 1
    recent = store.recent(5)
    assert recent[0]["risk"] == 0.21
    summary = store.summary()
    assert summary["decision_count"] == 1
    assert summary["severity_counts"]["high"] == 1
