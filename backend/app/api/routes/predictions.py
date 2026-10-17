from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.prediction import FarmPredictionsResponse, NodePredictionsResponse
from app.services.node_service import NodeService
from app.api.deps import get_current_user_optional
from app.models.user import User

router = APIRouter(tags=["Predictions"])


@router.get("/farms/{farm_id}/predictions", response_model=FarmPredictionsResponse, summary="Get historical disease predictions for a farm")
def get_farm_predictions(
    farm_id: int,
    limit: int = Query(50, ge=1, le=500, description="Max predictions to return"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Returns recent ML disease predictions across all nodes on the farm,
    including confidence scores, timestamp windows, and class probabilities.
    """
    service = NodeService(db)
    return service.get_farm_predictions(farm_id=farm_id, limit=limit, current_user=current_user)
