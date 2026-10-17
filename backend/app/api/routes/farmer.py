from typing import Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.dashboard import FarmerDashboardResponse, FarmerSystemOverviewResponse
from app.services.farmer_dashboard_service import FarmerDashboardService
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/farmer", tags=["Farmer"])


@router.get("/dashboard/{farm_id}", response_model=FarmerDashboardResponse, summary="Get combined Farmer Dashboard data")
def get_farmer_dashboard(
    farm_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns one combined dashboard response containing:
    - Farmer profile & farm details
    - Crop, coordinates, boundary
    - Overall health status
    - Latest node states (battery, signal, readings)
    - Latest prediction & confidence
    - All node predictions
    - Detected diseases
    - Localization & affected zone
    - Environmental parameters & wind
    - Latest agronomic recommendation
    - Active alerts & unread count
    """
    service = FarmerDashboardService(db)
    return service.get_dashboard(farm_id=farm_id, current_user=current_user)


@router.get("/system/{farm_id}", response_model=FarmerSystemOverviewResponse, summary="Get Farmer System Overview")
def get_farmer_system_overview(
    farm_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns summary of:
    - Node 1, Node 2, Node 3 details (battery, status, signal, sensor state, device temp, voltage, readings)
    - 5G/connectivity summary (status, carrier, latency, signal, packet statistics, uptime, module status)
    - Wind summary (speed, direction, angle)
    - Environment summary (temp, humidity, pressure, soil moisture)
    - Farm health (status, conditions)
    - Latest activity
    """
    service = FarmerDashboardService(db)
    return service.get_system_overview(farm_id=farm_id, current_user=current_user)
