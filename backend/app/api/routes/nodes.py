from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.node import NodeCreate, NodeUpdate, NodeOut
from app.schemas.node_history import NodeHistoryResponse
from app.schemas.prediction import NodePredictionsResponse, PredictionItem
from app.services.node_service import NodeService
from app.api.deps import get_current_user, get_current_user_optional
from app.models.user import User

router = APIRouter(prefix="/nodes", tags=["Nodes"])


@router.post("", response_model=NodeOut, status_code=status.HTTP_201_CREATED, summary="Register a new sensor node to a farm")
def create_node(
    node_in: NodeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Registers a new node (e.g. node_1, node_2, node_3) on a farm.
    Validates that the farm does not exceed its maximum capacity of 3 nodes.
    Stores authoritative GPS coordinates directly in MySQL.
    """
    service = NodeService(db)
    return service.create_node(node_in, current_user=current_user)


@router.api_route("/check-overdue", methods=["GET", "POST"], summary="Run hourly missing node check")
def check_overdue_nodes(
    farm_id: Optional[int] = Query(None, description="Optional farm_id to check"),
    db: Session = Depends(get_db)
):
    """
    Executes database-driven hourly missing node monitoring.
    Creates NODE_NO_DATA alerts for any nodes overdue for sensor ingestion.
    """
    from app.services.sensor_service import SensorDataService
    sensor_service = SensorDataService(db)
    return sensor_service.check_overdue_nodes(farm_id_input=farm_id)


@router.get("/{node_id}", response_model=NodeOut, summary="Get node telemetry and configuration")
def get_node(
    node_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Fetches node details including authoritative latitude/longitude, battery, signal strength,
    firmware version, and last seen timestamp.
    """
    service = NodeService(db)
    return service.get_node_by_id(node_id, current_user=current_user)


@router.put("/{node_id}", response_model=NodeOut, summary="Update node configuration or coordinates")
def update_node(
    node_id: str,
    node_in: NodeUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Updates node attributes such as authoritative GPS coordinates, firmware version,
    assigned farm, or master/slave status.
    """
    service = NodeService(db)
    return service.update_node(node_id, node_in, current_user=current_user)


@router.delete("/{node_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Decommission/delete a node")
def delete_node(
    node_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Decommissions a sensor node from the farm.
    """
    service = NodeService(db)
    service.delete_node(node_id, current_user=current_user)
    return None


@router.get("/{node_id}/history", response_model=NodeHistoryResponse, summary="Get historical cycle readings for a node")
def get_node_history(
    node_id: str,
    limit: int = Query(50, ge=1, le=500, description="Max number of cycles to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns time-series history for a node with temperature, humidity, pressure,
    battery, signal, and all 10 gas sensor readings per cycle.
    """
    service = NodeService(db)
    return service.get_node_history(node_id=node_id, limit=limit, current_user=current_user)


@router.get("/{node_id}/predictions", response_model=List[PredictionItem], summary="Get ML inference predictions for a node")
def get_node_predictions(
    node_id: str,
    limit: int = Query(50, ge=1, le=500, description="Max predictions to return"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Returns ML disease predictions for the specified node with confidence,
    anomaly score, and class probabilities.
    """
    service = NodeService(db)
    result = service.get_node_predictions(node_id=node_id, limit=limit, current_user=current_user)
    return result.predictions
