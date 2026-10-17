from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class AlertItem(BaseModel):
    alert_id: int
    farm_id: int
    node_id: Optional[str] = None
    type: str = Field(..., alias="type")
    alert_type: Optional[str] = None
    severity: str
    title: str
    message: str
    created_at: datetime
    is_read: bool
    is_acknowledged: Optional[bool] = False

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class FarmAlertsResponse(BaseModel):
    farm_id: int
    total: int
    unread_count: int
    alerts: List[AlertItem] = Field(default_factory=list)


class NodeAlertsResponse(BaseModel):
    node_id: str
    total: int
    unread_count: int
    alerts: List[AlertItem] = Field(default_factory=list)


class MarkAlertReadResponse(BaseModel):
    success: bool = True
    alert_id: int
    is_read: bool = True
    message: str = "Alert marked as read"
