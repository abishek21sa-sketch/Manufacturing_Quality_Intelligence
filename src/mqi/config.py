from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

@dataclass(frozen=True)
class Settings:
    seed: int = 42
    defect_threshold: float = 0.35
    model_path: Path = ROOT / "models" / "defect_model.joblib"
    artifact_dir: Path = ROOT / "artifacts"
    data_dir: Path = ROOT / "data"
    decision_db_path: Path = ROOT / "data" / "runtime" / "quality_decisions.sqlite3"

settings = Settings()
