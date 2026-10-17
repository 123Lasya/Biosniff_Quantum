from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str = "Operation successful"
    data: Optional[T] = None


class HealthResponse(BaseModel):
    status: str
    database: str
    version: str = "1.0.0"
    environment: str
    timestamp: str
