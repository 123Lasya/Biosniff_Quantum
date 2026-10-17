from typing import Optional, List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.admin import (
    AdminDashboardResponse,
    AdminFarmMapItem,
    AdminFarmersListResponse,
    AdminFarmerProfileResponse,
    AdminNodeListItem,
)

from app.services.admin_service import AdminService
from app.api.deps import get_current_admin
from app.models.user import User

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/dashboard", response_model=AdminDashboardResponse, summary="Get high-level aggregated administrative dashboard stats")
def get_admin_dashboard(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Computes and returns national/administrative telemetry and operational metrics strictly from MySQL:
    - total farmers, farms (active/inactive)
    - farm health status distribution (healthy, diseased, at-risk)
    - active & offline nodes count
    - active alerts count
    - network health (online percentage, average latency, packet loss)
    - regional/state-level farm distribution
    - crops monitored distribution
    - recent activities and alerts
    """
    service = AdminService(db)
    return service.get_dashboard()


@router.get("/farms/map", response_model=List[AdminFarmMapItem], summary="Get geospatial map data for all registered farms across India")
def get_admin_farms_map(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Returns geographical coordinates, crop metadata, active status, and real-time disease status
    for all monitored farms across India.
    """
    service = AdminService(db)
    return service.get_farms_map()


@router.get("/farmers", response_model=AdminFarmersListResponse, summary="List and filter all registered farmers")
def get_admin_farmers(
    search: Optional[str] = Query(None, description="Search by farmer name, email, or phone"),
    state: Optional[str] = Query(None, description="Filter by state (e.g. Maharashtra, Punjab)"),
    district: Optional[str] = Query(None, description="Filter by district"),
    crop: Optional[str] = Query(None, description="Filter by crop (e.g. Rice, Wheat)"),
    health: Optional[str] = Query(None, description="Filter by health status (healthy, diseased)"),
    status: Optional[str] = Query(None, description="Filter by status (Active, Inactive)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Page size"),
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Paginated farmer directory with full search, state/district filtering, crop filtering,
    and aggregate farm health status.
    """
    service = AdminService(db)
    return service.get_farmers_list(
        search=search,
        state=state,
        district=district,
        crop=crop,
        health=health,
        status_filter=status,
        page=page,
        page_size=page_size
    )


@router.get("/farmers/{farmer_id}", response_model=AdminFarmerProfileResponse, summary="Get full admin profile for a specific farmer")
def get_admin_farmer_profile(
    farmer_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Retrieves full administrative profile for a farmer including all their farms, total acreage,
    crops, locations, node statuses, recent predictions, environment data, alerts, and advisories.
    """
    service = AdminService(db)
    return service.get_farmer_profile(farmer_id=farmer_id)


@router.get("/nodes", response_model=List[AdminNodeListItem], summary="Get list of all sensor nodes across all farms for admin")
def get_admin_nodes(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Returns list of all deployed hardware nodes across all farms with farm, farmer, signal, battery,
    and latest telemetry readings.
    """
    service = AdminService(db)
    return service.get_all_nodes()

