from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class EnvironmentCurrentResponse(BaseModel):
    farm_id: int
    temperature: float = Field(..., description="Ambient temperature in °C")
    humidity: float = Field(..., description="Relative humidity in %")
    pressure: Optional[float] = Field(None, description="Atmospheric pressure in hPa")
    wind_speed: float = Field(0.0, description="Wind speed in m/s")
    wind_direction: Optional[str] = Field(None, description="Wind direction (e.g. 'NE (48°)' or 'NE')")
    wind_angle: Optional[float] = Field(None, description="Wind angle in degrees (0-360)")
    soil_moisture: Optional[float] = Field(None, description="Soil moisture in %")
    solar_radiation: Optional[float] = Field(None, description="Solar radiation in W/m²")
    weather_condition: Optional[str] = Field("Partly cloudy", description="Estimated weather condition")
    recorded_at: Optional[datetime] = None
    latest_reading: Optional[Dict[str, Any]] = None
    node_averages: Optional[Dict[str, Optional[float]]] = None

    model_config = ConfigDict(from_attributes=True)


class EnvironmentHistoryItem(BaseModel):
    timestamp: datetime
    temperature: float
    humidity: float
    pressure: Optional[float] = None
    wind_speed: float = 0.0
    wind_direction: Optional[str] = None
    wind_angle: Optional[float] = None
    soil_moisture: Optional[float] = None


class EnvironmentHistoryResponse(BaseModel):
    farm_id: int
    count: int
    history: List[EnvironmentHistoryItem] = Field(default_factory=list)
