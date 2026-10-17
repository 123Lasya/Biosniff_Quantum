from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.recommendation import Recommendation


class RecommendationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        farm_id: int,
        disease_name: str,
        title: str,
        details: str,
        action_type: str = "treatment",
        dosage: Optional[str] = None,
        urgency: str = "immediate",
        prediction_id: Optional[int] = None
    ) -> Recommendation:
        rec = Recommendation(
            farm_id=farm_id,
            prediction_id=prediction_id,
            disease_name=disease_name,
            title=title,
            action_type=action_type,
            details=details,
            dosage=dosage,
            urgency=urgency,
            is_applied=False,
            created_at=datetime.now(timezone.utc)
        )
        self.db.add(rec)
        self.db.commit()
        self.db.refresh(rec)
        return rec

    def get_by_farm_id(self, farm_id: int, limit: int = 50) -> List[Recommendation]:
        return self.db.query(Recommendation).filter(
            Recommendation.farm_id == farm_id
        ).order_by(Recommendation.created_at.desc()).limit(limit).all()

    def get_latest_for_farm(self, farm_id: int) -> Optional[Recommendation]:
        return self.db.query(Recommendation).filter(
            Recommendation.farm_id == farm_id
        ).order_by(Recommendation.created_at.desc()).first()
