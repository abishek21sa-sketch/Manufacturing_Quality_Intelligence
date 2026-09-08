from pydantic import BaseModel, Field

class ProcessObservation(BaseModel):
    temperature_c: float
    pressure_bar: float
    speed_mpm: float
    vibration_mm_s: float
    tool_wear_pct: float = Field(ge=0, le=100)
    material_hardness: float
    humidity_pct: float
    operator_experience_y: float

class CapabilityRequest(BaseModel):
    values: list[float]
    lsl: float
    usl: float

class SimulationRequest(BaseModel):
    defect_probability: float = Field(ge=0, le=1)
    volume: int = Field(gt=0)
    trials: int = Field(default=5000, ge=100, le=100000)

class InspectionRequest(BaseModel):
    defect_probability: float = Field(ge=0, le=1)
    volume: int = Field(gt=0)
    max_inspections: int | None = Field(default=None, ge=0)

class AdvancedSPCRequest(BaseModel):
    values: list[float]
    baseline_size: int | None = Field(default=None, ge=5)

class DriftRequest(BaseModel):
    reference: list[ProcessObservation]
    current: list[ProcessObservation]

class AdaptiveInspectionRequest(BaseModel):
    prior_bad: list[float]
    transitions: list[list[list[float]]]
    sensitivity: list[list[float]]
    specificity: list[list[float]]
    inspection_cost: list[list[float]]
    capacity_use: list[int]
    escape_cost: list[float]
    correction_cost: list[float]
    horizon: int = Field(default=3, ge=1, le=8)
    capacity_per_period: int = Field(default=2, ge=0, le=50)
