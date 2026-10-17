from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.connectivity import (
    ConnectivityCurrentResponse,
    ConnectivityHistoryResponse,
)
from app.services.connectivity_service import ConnectivityService
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/farms", tags=["Connectivity"])


@router.get("/{farm_id}/connectivity", response_model=ConnectivityCurrentResponse, summary="Get current 5G gateway connectivity telemetry for a farm")
def get_farm_connectivity(
    farm_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns real-time gateway metrics including connection status, RSSI, carrier,
    latency, estimated speeds, uptime, and 5G module operational health.
    """
    service = ConnectivityService(db)
    return service.get_farm_connectivity(farm_id=farm_id, current_user=current_user)


@router.get("/{farm_id}/connectivity/history", response_model=ConnectivityHistoryResponse, summary="Get historical network connectivity metrics for a farm")
def get_farm_connectivity_history(
    farm_id: int,
    hours: int = Query(24, ge=1, le=168, description="History window in hours"),
    limit: int = Query(50, ge=1, le=200, description="Max records to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns time-series network performance data including latency curves and speed logs
    for connectivity monitoring.
    """
    service = ConnectivityService(db)
    return service.get_farm_connectivity_history(
        farm_id=farm_id,
        hours=hours,
        limit=limit,
        current_user=current_user
    )
