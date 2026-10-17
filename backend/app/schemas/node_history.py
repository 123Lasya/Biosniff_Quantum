from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class NodeHistoryItem(BaseModel):
    cycle_id: int
    node_id: str
    timestamp: datetime
    time: str
    cycle_number: int
    temperature: float
    humidity: float
    pressure: float
    battery: Optional[float] = None
    signal: Optional[float] = None
    gas_readings: List[float] = Field(default_factory=list)
    R1: Optional[float] = None
    R2: Optional[float] = None
    R3: Optional[float] = None
    R4: Optional[float] = None
    R5: Optional[float] = None
    R6: Optional[float] = None
    R7: Optional[float] = None
    R8: Optional[float] = None
    R9: Optional[float] = None
    R10: Optional[float] = None


class NodeHistoryResponse(BaseModel):
    node_id: str
    farm_id: int
    count: int
    history: List[NodeHistoryItem] = Field(default_factory=list)
