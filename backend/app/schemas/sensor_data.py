from typing import List, Optional, Union, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator


class WindPayload(BaseModel):
    average_speed: float = Field(..., description="Average wind speed in m/s (must be >= 0)")
    average_direction: float = Field(..., description="Average wind direction in degrees (0 to 360)")

    @field_validator("average_speed")
    @classmethod
    def validate_speed(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Wind average_speed must be non-negative (>= 0)")
        return v

    @field_validator("average_direction")
    @classmethod
    def validate_direction(cls, v: float) -> float:
        if v < 0 or v > 360:
            raise ValueError("Wind average_direction must be within [0, 360] degrees")
        return v


class NodeCyclePayload(BaseModel):
    node_id: str = Field(..., description="Hardware identifier of the sensing node (e.g. NODE_01)")
    gas_resistance: Any = Field(..., description="Array of exactly 10 gas resistance readings")
    temperature: Any = Field(..., description="Ambient temperature reading (°C)")
    humidity: Any = Field(..., description="Ambient relative humidity (%)")
    pressure: Any = Field(..., description="Barometric pressure (hPa)")
    battery: Optional[Any] = Field(None, description="Battery percentage (0-100)")
    signal: Optional[Any] = Field(None, description="Signal strength RSSI (dBm)")

    model_config = ConfigDict(extra="ignore")


class MasterSensorPayload(BaseModel):
    """
    Combined hourly payload transmitted by the Master ESP32 Gateway.
    Contains telemetry from connected nodes and microclimate wind measurements.
    """
    farm_id: Union[int, str] = Field(..., description="Target Farm ID (e.g. 1 or 'FARM_001')")
    timestamp: datetime = Field(..., description="Timestamp of the hourly cycle (ISO-8601)")
    nodes: List[NodeCyclePayload] = Field(default_factory=list, description="List of node cycles in this hourly batch")
    wind: Optional[WindPayload] = Field(None, description="Wind measurements (speed and direction)")

    model_config = ConfigDict(extra="ignore")


class NodePredictionResult(BaseModel):
    prediction_id: Optional[int] = None
    node_id: str
    farm_id: int
    predicted_class: str
    is_disease: bool
    confidence: float
    probabilities: Dict[str, float]
    window_start: datetime
    window_end: datetime
    model_version: str
    cycle_ids: List[int] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class ProcessedNodeResult(BaseModel):
    node_id: str
    status: str = "saved"
    cycle_id: int
    cycle_number: int
    prediction_ready: bool
    readiness_status: str
    cycles_available: int
    cycles_required: int = 5
    latest_5_cycle_ids: List[int] = Field(default_factory=list)
    prediction: Optional[NodePredictionResult] = None


class RejectedNodeResult(BaseModel):
    node_id: str
    status: str = "rejected"
    reason: str


class MissingNodeResult(BaseModel):
    node_id: str
    status: str = "missing_in_batch"
    alert_created: bool = True
    message: str


class SensorDataIngestResponse(BaseModel):
    status: str  # "success", "partial_success", "duplicate", "error"
    message: str
    farm_id: int
    timestamp: datetime
    processed_nodes: List[ProcessedNodeResult] = Field(default_factory=list)
    rejected_nodes: List[RejectedNodeResult] = Field(default_factory=list)
    missing_nodes: List[MissingNodeResult] = Field(default_factory=list)
    environment_saved: bool = False
    predictions: List[NodePredictionResult] = Field(default_factory=list)
    farm_disease_status: str = "healthy"  # "healthy" or "disease_detected"
    localization_activated: bool = False
    localization: Optional[Dict[str, Any]] = None
    recommendations: List[Dict[str, Any]] = Field(default_factory=list)
    alerts: List[Dict[str, Any]] = Field(default_factory=list)
    detected_conditions: List[str] = Field(default_factory=list)
    summary: Dict[str, int] = Field(default_factory=dict)


class SensorCycleItem(BaseModel):
    cycle_id: int
    node_id: str
    farm_id: int
    cycle_timestamp: datetime
    cycle_number: int
    gas_readings: List[float]
    temperature: float
    humidity: float
    pressure: float
    battery: Optional[float] = None
    signal: Optional[float] = None
    is_valid: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NodeSensorHistoryResponse(BaseModel):
    node_id: str
    farm_id: int
    node_name: str
    status: str
    battery_percentage: float
    signal_strength: float
    last_seen: Optional[datetime]
    total_cycles: int
    prediction_ready: bool
    readiness_status: str
    cycles_available: int
    cycles_required: int = 5
    latest_5_window: List[SensorCycleItem] = Field(default_factory=list)
    cycles: List[SensorCycleItem] = Field(default_factory=list)


class EnvironmentReadingItem(BaseModel):
    reading_id: int
    farm_id: int
    node_id: Optional[str] = None
    wind_speed: float
    wind_direction: Optional[str] = None
    ambient_temp: float
    humidity: float
    pressure: Optional[float] = None
    soil_moisture: Optional[float] = None
    recorded_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FarmEnvironmentCurrentResponse(BaseModel):
    farm_id: int
    farm_name: str
    latest_reading: Optional[EnvironmentReadingItem] = None
    node_averages: Optional[Dict[str, Optional[float]]] = None
    status: str = "operational"


class FarmEnvironmentHistoryResponse(BaseModel):
    farm_id: int
    count: int
    history: List[EnvironmentReadingItem] = Field(default_factory=list)


class FarmPredictionsResponse(BaseModel):
    farm_id: int
    farm_name: str
    farm_disease_status: str  # "healthy" or "disease_detected"
    localization_activated: bool
    predictions: List[NodePredictionResult] = Field(default_factory=list)

