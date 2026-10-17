from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.environment import (
    EnvironmentCurrentResponse,
    EnvironmentHistoryResponse,
)
from app.services.environment_service import EnvironmentService
from app.api.deps import get_current_user_optional
from app.models.user import User

router = APIRouter(prefix="/farms", tags=["Environment"])


@router.get("/{farm_id}/environment", response_model=EnvironmentCurrentResponse, summary="Get current microclimate and environmental telemetry for a farm")
def get_farm_environment(
    farm_id: int,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Returns current ambient conditions for the farm including temperature, humidity,
    atmospheric pressure, wind speed, wind direction, soil moisture, and solar radiation.
    """
    service = EnvironmentService(db)
    return service.get_farm_environment(farm_id=farm_id, current_user=current_user)


@router.get("/{farm_id}/environment/history", response_model=EnvironmentHistoryResponse, summary="Get historical environmental readings for a farm")
def get_farm_environment_history(
    farm_id: int,
    hours: int = Query(24, ge=1, le=168, description="History window in hours"),
    limit: int = Query(100, ge=1, le=500, description="Max records to return"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Returns time-series environmental observations (temperature, humidity, pressure, wind)
    for chart rendering and climate trend analysis.
    """
    service = EnvironmentService(db)
    return service.get_farm_environment_history(
        farm_id=farm_id,
        hours=hours,
        limit=limit,
        current_user=current_user
    )
