from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db
from app.core.config import settings
from app.schemas.common import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)):
    """
    Evaluates backend service health and confirms database connectivity.
    """
    db_status = "connected"
    try:
        # Executes lightweight ping query compatible with both MySQL and SQLite
        db.execute(text("SELECT 1"))
    except Exception as exc:
        db_status = f"unhealthy: {str(exc)}"

    return HealthResponse(
        status="healthy" if db_status == "connected" else "degraded",
        database=db_status,
        version="1.0.0",
        environment=settings.ENVIRONMENT,
        timestamp=datetime.now(timezone.utc).isoformat()
    )
