from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class NodeBase(BaseModel):
    node_name: str = Field(..., min_length=2, max_length=100)
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Authoritative GPS latitude")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Authoritative GPS longitude")
    status: str = Field(default="online", max_length=50)
    battery_percentage: float = Field(default=100.0, ge=0.0, le=100.0)
    signal_strength: float = Field(default=-65.0, description="Signal strength RSSI in dBm")
    firmware_version: str = Field(default="v1.2.4-mesh", max_length=50)
    is_master: bool = False


class NodeCreate(NodeBase):
    node_id: str = Field(..., min_length=2, max_length=50, description="Unique node identifier e.g. node_1")
    farm_id: int


class NodeUpdate(BaseModel):
    node_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    status: Optional[str] = None
    battery_percentage: Optional[float] = None
    signal_strength: Optional[float] = None
    firmware_version: Optional[str] = None
    is_master: Optional[bool] = None
    farm_id: Optional[int] = None


class NodeStatusUpdate(BaseModel):
    status: Optional[str] = None
    battery_percentage: Optional[float] = None
    signal_strength: Optional[float] = None
    firmware_version: Optional[str] = None


class NodeOut(NodeBase):
    node_id: str
    farm_id: int
    last_seen: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    # Frontend-friendly and detailed telemetry fields
    battery: Optional[float] = None
    signal: Optional[str] = None
    signal_dbm: Optional[float] = None
    coordinates: Optional[Dict[str, float]] = None
    hardware: Optional[str] = "ESP32 + BME688"
    power_source: Optional[str] = "Solar (with Battery)"
    device_temp: Optional[float] = None
    battery_voltage: Optional[float] = 5.0
    uptime: Optional[str] = "98% (7 days)"
    readings: Optional[Dict[str, Any]] = None
    transmission_logs: Optional[List[Dict[str, Any]]] = None

    model_config = ConfigDict(from_attributes=True)
