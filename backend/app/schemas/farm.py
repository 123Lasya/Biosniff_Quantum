from typing import Optional, List, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class FarmBase(BaseModel):
    farm_name: str = Field(..., min_length=2, max_length=150)
    area: float = Field(..., ge=0.0, description="Area in acres")
    crop: str = Field(default="Rice (Paddy)", max_length=100)
    crop_variety: Optional[str] = None
    growth_stage: Optional[str] = Field(default="Vegetative", max_length=100)
    address: Optional[str] = None
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    boundary_geojson: Optional[str] = None
    status: str = Field(default="active", max_length=50)


class FarmCreate(FarmBase):
    farmer_id: Optional[int] = None  # Inferred from authenticated farmer if omitted


class FarmUpdate(BaseModel):
    farm_name: Optional[str] = None
    area: Optional[float] = None
    crop: Optional[str] = None
    crop_variety: Optional[str] = None
    growth_stage: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    boundary_geojson: Optional[str] = None
    status: Optional[str] = None


class FarmOut(FarmBase):
    farm_id: int
    farmer_id: int
    node_count: Optional[int] = 0
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FarmDetailOut(FarmOut):
    nodes: List[Any] = []
