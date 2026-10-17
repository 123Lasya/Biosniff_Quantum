from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class PredictionItem(BaseModel):
    prediction_id: int
    node_id: str
    farm_id: int
    cycle_id: int
    timestamp: datetime
    window_start: Optional[datetime] = None
    window_end: Optional[datetime] = None
    predicted_class: str
    disease_detected: bool
    confidence: float
    anomaly_score: Optional[float] = None
    all_class_probabilities: Optional[Dict[str, float]] = None
    model_version: str

    model_config = ConfigDict(from_attributes=True)


class FarmPredictionsResponse(BaseModel):
    farm_id: int
    count: int
    predictions: List[PredictionItem] = Field(default_factory=list)
    farm_disease_status: Optional[str] = "Healthy"
    localization_activated: Optional[bool] = False
    detected_diseases: Optional[List[str]] = Field(default_factory=list)


class NodePredictionsResponse(BaseModel):
    node_id: str
    farm_id: int
    count: int
    predictions: List[PredictionItem] = Field(default_factory=list)
