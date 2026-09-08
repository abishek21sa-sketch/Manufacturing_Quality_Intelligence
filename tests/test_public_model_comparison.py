from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from empirical.public_data_backbone import data_backbone_status
from fastapi.testclient import TestClient
from mqi.service.api import app


def test_uci_steel_backbone_is_active_and_compares_models():
    status = data_backbone_status()
    assert status["dataset"] == "UCI Steel Plates Faults"
    assert status["dataset_state"] == "REFRESHED_EXTERNAL_ACTIVE"
    case = status["case_study"]
    assert case["status"] == "ACTIVE"
    model = case["defect_risk_model"]
    names = {row["model"] for row in model["model_comparison"]}
    assert {"constant_prevalence_baseline", "nearest_centroid_challenger", "class_balanced_logistic_champion"} <= names
    assert model["selected_model"] in names
    assert model["holdout"]["rows"] > 0


def test_public_model_comparison_api_is_frontend_ready():
    response = TestClient(app).get("/v1/public-data/model-comparison")
    assert response.status_code == 200
    body = response.json()
    assert body["dataset"] == "UCI Steel Plates Faults"
    assert body["comparison"]
    assert body["selected_model"] == "class_balanced_logistic_champion"
