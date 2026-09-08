from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from mqi.config import settings
from mqi.ai.model import load_model
from mqi.ai.monitoring import drift_report
from mqi.data.synthetic import FEATURES, generate_process_data
from mqi.decision.engine import recommend
from mqi.optimization.inspection import optimize_inspection
from mqi.optimization.signature_algorithm import choose_inspection as signature_choose, ablation as signature_ablation, sensitivity as signature_sensitivity
from mqi.optimization.msa_pomdp import solve_multiline_inspection_pomdp, no_inspection_expected_cost
from mqi.persistence import DecisionStore
from mqi.governance import build_inspection_certificate, verify_inspection_certificate
from empirical.public_data_backbone import data_backbone_status
from mqi.quality.advanced_spc import cusum_chart, ewma_chart, hotelling_t2
from mqi.quality.spc import capability, individuals_chart, detect_rule1
from mqi.service.schemas import (
    ProcessObservation, CapabilityRequest, SimulationRequest, InspectionRequest,
    AdvancedSPCRequest, DriftRequest, AdaptiveInspectionRequest,
)
from mqi.copilot import build_response as build_copilot_response, status as copilot_status
from mqi.simulation.monte_carlo import simulate_quality

app = FastAPI(title="Manufacturing Quality Intelligence Platform", version="1.6.0")

@app.middleware("http")
async def request_context(request, call_next):
    request_id=request.headers.get("X-Request-ID") or f"mqi-{uuid.uuid4().hex[:16]}"
    started=time.perf_counter()
    response=await call_next(request)
    response.headers["X-Request-ID"]=request_id
    response.headers["X-Response-Time-Ms"]=f"{(time.perf_counter()-started)*1000:.3f}"
    response.headers["X-Quality-Policy-Execution"]="REVIEW_ONLY"
    return response
STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

class CopilotRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)

@app.get("/v1/copilot/status")
def copilot_runtime_status():
    return copilot_status()

@app.post("/v1/copilot/chat")
def copilot_chat(req: CopilotRequest):
    return build_copilot_response(req.message, {"evidence": "MQI model, SPC, capability, MSA, public Steel Plates comparison, and inspection optimization", "mode": "review-only"})

_model = None
_store = DecisionStore(settings.decision_db_path)

def get_model():
    global _model
    if _model is None:
        if not settings.model_path.exists():
            raise HTTPException(503, "Model not trained. Run `mqi bootstrap` first.")
        _model = load_model(settings.model_path)
    return _model

@app.get("/")
def home():
    return FileResponse(STATIC_DIR / "index.html")

@app.get("/health")
def health():
    return {"status": "ok", "model_ready": settings.model_path.exists(), "version": "1.6.0", "decision_store": True, "adaptive_inspection_pomdp": True}


@app.get("/v1/governance/signature")
def governance_signature():
    """Expose the executable ECON-SPC-P reference policy and counterfactuals."""
    args = ([0.8, 0.2], [0.95, 0.90], [0.95, 0.95], [2, 2], [100, 100], 1)
    selected = signature_choose(*args)
    baseline = {"actions": [0, 0], "expected_cost": sum(p * e for p, e in zip(args[0], args[4]))}
    return {
        "status": "HUMAN_GATED_REFERENCE",
        "signature_algorithm": "ECON-SPC-P",
        "decision": selected,
        "baseline": baseline,
        "ablation": signature_ablation(*args),
        "sensitivity": signature_sensitivity(*args, capacity_delta=1),
        "objective": "minimize expected inspection plus escape cost",
        "counterfactual": "non-informative gage ablation",
        "evidence_artifact": "artifacts/fortune50_capability_benchmark.json",
        "autonomous_execution": False,
    }

@app.get("/v1/evidence")
def evidence():
    path = settings.artifact_dir / "validation_report.json"
    if not path.exists():
        raise HTTPException(404, "Validation evidence unavailable; run `mqi bootstrap`.")
    return json.loads(path.read_text())

@app.get("/v1/public-data/model-comparison")
def public_data_model_comparison():
    """Return the reproducible public-data model leaderboard for the MQI evidence UI."""
    status = data_backbone_status()
    case = status.get("case_study", {})
    model = case.get("defect_risk_model", {})
    if case.get("status") != "ACTIVE" or not model:
        raise HTTPException(503, "Public Steel Plates Faults evidence is not active")
    return {
        "dataset": status.get("dataset"),
        "dataset_state": status.get("dataset_state"),
        "primary_files": status.get("primary_files"),
        "claim_boundary": status.get("claim_boundary"),
        "comparison": model.get("model_comparison", []),
        "selected_model": model.get("selected_model"),
        "selection_metric": model.get("selection_metric"),
        "target": model.get("target"),
        "holdout_rows": model.get("holdout", {}).get("rows"),
    }

@app.post("/v1/predict")
def predict(obs: ProcessObservation):
    model = get_model()
    row = pd.DataFrame([obs.model_dump()])
    probability = float(model.predict_proba(row[FEATURES])[0, 1])
    return {"defect_probability": probability}

@app.post("/v1/decision")
def decision(obs: ProcessObservation, volume: int = Query(default=1000, gt=0, le=1_000_000)):
    model = get_model()
    request = obs.model_dump()
    row = pd.DataFrame([request])
    payload = recommend(model, row[FEATURES], volume=volume).__dict__
    payload["decision_id"] = _store.record({**request, "volume": volume}, payload)
    return payload

@app.get("/v1/decisions")
def recent_decisions(limit: int = Query(default=20, ge=1, le=200)):
    return {"summary": _store.summary(), "items": _store.recent(limit)}

@app.post("/v1/capability")
def capability_api(req: CapabilityRequest):
    return capability(req.values, req.lsl, req.usl).__dict__

@app.get("/v1/spc/demo")
def spc_demo():
    df = generate_process_data(600, seed=7)
    baseline = df["dimension_error_mm"].iloc[:300]
    limits = individuals_chart(baseline)
    signals = detect_rule1(df["dimension_error_mm"].iloc[300:], limits)
    multi = hotelling_t2(df[FEATURES].iloc[:300], df[FEATURES].iloc[300:])
    return {"limits": limits.__dict__, "signals_after_baseline": signals[:50], "signal_count": len(signals),
            "multivariate_signal_count": len(multi.signals), "hotelling_threshold": multi.threshold}

@app.post("/v1/spc/advanced")
def advanced_spc(req: AdvancedSPCRequest):
    ewma = ewma_chart(req.values, req.baseline_size)
    cusum = cusum_chart(req.values, req.baseline_size)
    return {
        "ewma": {"center": ewma.center, "lambda": ewma.lambda_, "signal_count": len(ewma.signals), "signals": ewma.signals},
        "cusum": {"target": cusum.target, "k": cusum.k, "h": cusum.h, "signal_count": len(cusum.signals), "signals": cusum.signals},
    }

@app.post("/v1/monitoring/drift")
def drift(req: DriftRequest):
    reference = pd.DataFrame([x.model_dump() for x in req.reference])
    current = pd.DataFrame([x.model_dump() for x in req.current])
    return drift_report(reference, current, FEATURES).__dict__

@app.post("/v1/simulate")
def simulate(req: SimulationRequest):
    return simulate_quality(req.defect_probability, req.volume, req.trials).__dict__

@app.post("/v1/optimize-inspection")
def optimize(req: InspectionRequest):
    return optimize_inspection(req.defect_probability, req.volume, max_inspections=req.max_inspections).__dict__


@app.post("/v1/optimize-adaptive-inspection")
def optimize_adaptive_inspection(req: AdaptiveInspectionRequest):
    """Solve the MSA-aware finite-horizon multi-line inspection POMDP.

    The endpoint returns a decision policy only; it does not authorize changes on a
    production inspection line.
    """
    try:
        prior=np.asarray(req.prior_bad,float)
        transitions=np.asarray(req.transitions,float)
        sensitivity=np.asarray(req.sensitivity,float)
        specificity=np.asarray(req.specificity,float)
        inspection_cost=np.asarray(req.inspection_cost,float)
        capacity_use=np.asarray(req.capacity_use,int)
        escape_cost=np.asarray(req.escape_cost,float)
        correction_cost=np.asarray(req.correction_cost,float)
        result=solve_multiline_inspection_pomdp(
            prior, transitions, sensitivity, specificity, inspection_cost, capacity_use,
            escape_cost=escape_cost, correction_cost=correction_cost, horizon=req.horizon,
            capacity_per_period=req.capacity_per_period,
        )
        baseline=no_inspection_expected_cost(prior,transitions,escape_cost,req.horizon)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    return {
        "method":"ECON-SPC-P MSA-aware finite-horizon inspection POMDP",
        "expected_cost":result.expected_cost,
        "no_inspection_expected_cost":baseline,
        "modeled_cost_avoidance":baseline-result.expected_cost,
        "first_action":list(result.first_action),
        "states_evaluated":result.states_evaluated,
        "production_write_allowed":False,
        "evidence_boundary":"Model-based expected quality economics; not realized plant savings.",
    }

@app.post("/v1/governance/adaptive-inspection-certificate")
def adaptive_inspection_certificate(req: AdaptiveInspectionRequest):
    solution=optimize_adaptive_inspection(req)
    certificate=build_inspection_certificate(request=req.model_dump(),solution=solution)
    return {"solution":solution,"certificate":certificate,"verification":verify_inspection_certificate(certificate)}
