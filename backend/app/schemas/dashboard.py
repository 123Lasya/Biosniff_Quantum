from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class Coordinates(BaseModel):
    lat: float
    lng: float


class FarmerDashboardResponse(BaseModel):
    farmer: Dict[str, Any]
    farm: Dict[str, Any]
    crop: str
    crop_variety: Optional[str] = None
    farm_coordinates: Coordinates
    farm_boundary: List[Coordinates] = Field(default_factory=list)
    health_status: str  # healthy, diseased, at-risk, inactive
    latest_node_states: List[Dict[str, Any]] = Field(default_factory=list)
    battery: Optional[float] = None
    signal: Optional[str] = None
    latest_prediction: Optional[Dict[str, Any]] = None
    confidence: Optional[float] = None
    all_node_predictions: List[Dict[str, Any]] = Field(default_factory=list)
    detected_diseases: List[str] = Field(default_factory=list)
    disease_status: Optional[str] = "Healthy"
    localization: Optional[Dict[str, Any]] = None
    affected_zone: Optional[Dict[str, Any]] = None
    localized_source: Optional[Dict[str, Any]] = None
    wind: Optional[Dict[str, Any]] = None
    wind_speed: Optional[float] = None
    wind_direction: Optional[str] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    pressure: Optional[float] = None
    soil_moisture: Optional[float] = None

    weather_summary: Optional[Dict[str, Any]] = None
    alerts_summary: Optional[Dict[str, Any]] = None
    latest_recommendation: Optional[Dict[str, Any]] = None
    recommended_action_summary: Optional[str] = None
    prediction_trend_24h: List[Dict[str, Any]] = Field(default_factory=list)
    system_connectivity_summary: Optional[Dict[str, Any]] = None
    active_alerts: List[Dict[str, Any]] = Field(default_factory=list)
    unread_alerts_count: int = 0
    last_update: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class FarmerSystemOverviewResponse(BaseModel):
    farm_id: int
    nodes: Dict[str, Any]  # Node 1, Node 2, Node 3
    connectivity_summary: Dict[str, Any]  # 5G/connectivity summary
    wind_summary: Dict[str, Any]
    environment_summary: Dict[str, Any]
    farm_health: Dict[str, Any]
    latest_activity: List[Dict[str, Any]] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
