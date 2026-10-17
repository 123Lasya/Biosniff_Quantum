from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class AdminDashboardResponse(BaseModel):
    total_farmers: int
    total_farms: int
    active_farms: int
    inactive_farms: int
    healthy_farms: int
    diseased_farms: int
    at_risk_farms: int
    active_nodes: int
    offline_nodes: int
    active_alerts: int
    network_health: Dict[str, Any]
    regional_summaries: List[Dict[str, Any]] = Field(default_factory=list)
    crops_monitored: List[Dict[str, Any]] = Field(default_factory=list)
    recent_activity: List[Dict[str, Any]] = Field(default_factory=list)
    recent_alerts: List[Dict[str, Any]] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class AdminFarmMapItem(BaseModel):
    farm_id: int
    farm_name: str
    farmer: str
    state: Optional[str] = None
    district: Optional[str] = None
    latitude: float
    longitude: float
    crop: str
    crop_variety: Optional[str] = None
    area_acres: float
    health_status: str
    disease_status: str
    active_status: str
    status: str

    model_config = ConfigDict(from_attributes=True)


class AdminFarmersListResponse(BaseModel):
    items: List[Dict[str, Any]] = Field(default_factory=list)
    total: int
    page: int
    page_size: int
    total_pages: int


class AdminFarmerProfileResponse(BaseModel):
    farmer_details: Dict[str, Any]
    farms: List[Dict[str, Any]] = Field(default_factory=list)
    farm_areas: float
    crops: List[str] = Field(default_factory=list)
    locations: List[Dict[str, Any]] = Field(default_factory=list)
    health: str
    nodes: List[Dict[str, Any]] = Field(default_factory=list)
    alerts: List[Dict[str, Any]] = Field(default_factory=list)
    latest_predictions: List[Dict[str, Any]] = Field(default_factory=list)
    environment_summaries: List[Dict[str, Any]] = Field(default_factory=list)
    history_summaries: List[Dict[str, Any]] = Field(default_factory=list)
    advisories: List[Dict[str, Any]] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class AdminNodeListItem(BaseModel):
    node_id: str
    node_name: str
    farm_id: int
    farm_name: str
    farmer_id: int
    farmer_name: str
    latitude: float
    longitude: float
    status: str
    battery_percentage: Optional[float] = None
    signal_strength: Optional[int] = None
    firmware_version: Optional[str] = None
    is_master: bool = False
    last_seen: Optional[str] = None
    latest_temperature: Optional[float] = None
    latest_humidity: Optional[float] = None
    latest_pressure: Optional[float] = None
    latest_voc: Optional[float] = None
    latest_prediction: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

