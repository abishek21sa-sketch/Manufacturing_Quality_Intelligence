from __future__ import annotations

from dataclasses import dataclass
import pandas as pd

REQUIRED_PROCESS_COLUMNS = {
    "event_time", "part_id", "temperature_c", "pressure_bar", "speed_mpm",
    "vibration_mm_s", "tool_wear_pct", "defect"
}

@dataclass(frozen=True)
class DataQualityReport:
    rows: int
    missing_cells: int
    duplicate_part_ids: int
    invalid_defect_labels: int
    passed: bool


def validate_process_frame(df: pd.DataFrame) -> DataQualityReport:
    missing_cols = REQUIRED_PROCESS_COLUMNS - set(df.columns)
    if missing_cols:
        raise ValueError(f"Missing required columns: {sorted(missing_cols)}")
    invalid = int((~df["defect"].isin([0, 1])).sum())
    report = DataQualityReport(
        rows=len(df),
        missing_cells=int(df[list(REQUIRED_PROCESS_COLUMNS)].isna().sum().sum()),
        duplicate_part_ids=int(df["part_id"].duplicated().sum()),
        invalid_defect_labels=invalid,
        passed=bool(invalid == 0 and df["part_id"].duplicated().sum() == 0),
    )
    return report
