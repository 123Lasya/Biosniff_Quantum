from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class LocalCoordinate(BaseModel):
    x: float
    y: float


class GeoCoordinate(BaseModel):
    latitude: float
    longitude: float


class AffectedZone(BaseModel):
    center_x: float
    center_y: float
    radius_m: float
    geojson: Optional[Dict[str, Any]] = None


class LocalizationResponse(BaseModel):
    active: bool
    farm_local: Optional[LocalCoordinate] = None
    geo: Optional[GeoCoordinate] = None
    affected_zone: Optional[AffectedZone] = None
    trigger_nodes: List[str] = Field(default_factory=list)
    detected_conditions: List[str] = Field(default_factory=list)
    source_score: float = 0.0
    message: Optional[str] = None
    localization_id: Optional[int] = None
    timestamp: Optional[datetime] = None
    status: Optional[str] = "active"


class LocalizationHistoryItem(BaseModel):
    localization_id: int
    farm_id: int
    timestamp: datetime
    predicted_source_x: Optional[float]
    predicted_source_y: Optional[float]
    latitude: float
    longitude: float
    radius_m: float
    source_score: float
    trigger_nodes: List[str] = Field(default_factory=list)
    detected_conditions: List[str] = Field(default_factory=list)
    affected_zone: Optional[Dict[str, Any]] = None
    severity: str
    status: str

    model_config = ConfigDict(from_attributes=True)


class FarmLocalizationHistoryResponse(BaseModel):
    farm_id: int
    total: int
    history: List[LocalizationHistoryItem] = Field(default_factory=list)
