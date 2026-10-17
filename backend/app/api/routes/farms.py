from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.farm import FarmCreate, FarmUpdate, FarmOut
from app.schemas.node import NodeOut
from app.services.farm_service import FarmService
from app.services.node_service import NodeService
from app.api.deps import get_current_user
from app.models.user import User, UserRole
from app.models.farmer import Farmer

router = APIRouter(prefix="/farms", tags=["Farms"])


@router.get("", response_model=List[FarmOut], summary="List all farms accessible to current user")
def list_farms(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns list of farms. If current user is a Farmer, returns only farms owned by them.
    If current user is an Admin, returns all farms.
    """
    service = FarmService(db)
    if current_user.role == UserRole.ADMIN:
        farms = service.get_all_farms(skip=skip, limit=limit)
    else:
        farmer = db.query(Farmer).filter(Farmer.user_id == current_user.user_id).first()
        if not farmer:
            return []
        farms = service.get_farms_for_farmer(farmer.farmer_id)
    
    # Enrich with node counts
    result = []
    for f in farms:
        f_out = FarmOut.model_validate(f)
        f_out.node_count = len(f.nodes)
        result.append(f_out)
    return result


@router.post("", response_model=FarmOut, status_code=status.HTTP_201_CREATED, summary="Create a new farm")
def create_farm(
    farm_in: FarmCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Creates a new farm record linked to the authenticated farmer's profile.
    """
    service = FarmService(db)
    farm = service.create_farm(farm_in, current_user=current_user)
    f_out = FarmOut.model_validate(farm)
    f_out.node_count = 0
    return f_out


@router.get("/{farm_id}", response_model=FarmOut, summary="Get details of a specific farm")
def get_farm(
    farm_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves detailed metadata for a specific farm including authoritative coordinates and status.
    """
    service = FarmService(db)
    farm = service.get_farm_by_id(farm_id, current_user=current_user)
    f_out = FarmOut.model_validate(farm)
    f_out.node_count = len(farm.nodes)
    return f_out


@router.put("/{farm_id}", response_model=FarmOut, summary="Update farm details")
def update_farm(
    farm_id: int,
    farm_in: FarmUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Updates farm attributes (crop variety, growth stage, boundaries, status, coordinates).
    """
    service = FarmService(db)
    farm = service.update_farm(farm_id, farm_in, current_user=current_user)
    f_out = FarmOut.model_validate(farm)
    f_out.node_count = len(farm.nodes)
    return f_out


@router.delete("/{farm_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a farm")
def delete_farm(
    farm_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Deletes a farm record and cascades removal of associated nodes and telemetry.
    """
    service = FarmService(db)
    service.delete_farm(farm_id, current_user=current_user)
    return None


@router.get("/{farm_id}/nodes", response_model=List[NodeOut], summary="List all Bio-Sniff nodes deployed on a farm")
def get_farm_nodes(
    farm_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves all sensor nodes (up to 3) assigned to the farm, with authoritative GPS coordinates,
    battery percentage, signal strength, and online status.
    """
    service = NodeService(db)
    nodes = service.get_nodes_for_farm(farm_id, current_user=current_user)
    return nodes
