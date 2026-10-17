"""
Repository for storing and querying LSTM disease predictions.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from sqlalchemy import select, desc
from sqlalchemy.orm import Session

from app.models.prediction import Prediction


class PredictionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        node_id: str,
        farm_id: int,
        cycle_id: int,
        window_cycle_ids: List[int],
        predicted_class: str,
        disease_detected: bool,
        confidence: float,
        all_class_probabilities: Dict[str, float],
        model_version: str,
        window_start: Optional[datetime] = None,
        window_end: Optional[datetime] = None,
        anomaly_score: Optional[float] = None
    ) -> Prediction:
        """Stores a new model inference record."""
        now = datetime.now(timezone.utc)
        record = Prediction(
            node_id=node_id,
            farm_id=farm_id,
            cycle_id=cycle_id,
            window_cycle_ids=window_cycle_ids,
            predicted_class=predicted_class,
            disease_detected=disease_detected,
            confidence=confidence,
            raw_probabilities=all_class_probabilities,
            all_class_probabilities=all_class_probabilities,
            model_version=model_version,
            window_start=window_start,
            window_end=window_end,
            anomaly_score=anomaly_score,
            timestamp=now,
            created_at=now
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_by_id(self, prediction_id: int) -> Optional[Prediction]:
        stmt = select(Prediction).where(Prediction.prediction_id == prediction_id)
        return self.db.execute(stmt).scalars().first()

    def get_latest_by_node(self, node_id: str) -> Optional[Prediction]:
        stmt = (
            select(Prediction)
            .where(Prediction.node_id == node_id)
            .order_by(desc(Prediction.prediction_id))
            .limit(1)
        )
        return self.db.execute(stmt).scalars().first()

    def get_latest_by_farm(self, farm_id: int) -> List[Prediction]:
        """Returns the most recent prediction for each node registered to the farm."""
        stmt = (
            select(Prediction)
            .where(Prediction.farm_id == farm_id)
            .order_by(desc(Prediction.prediction_id))
            .limit(20)
        )
        return list(self.db.execute(stmt).scalars().all())

    def get_history_by_farm(self, farm_id: int, limit: int = 50) -> List[Prediction]:
        stmt = (
            select(Prediction)
            .where(Prediction.farm_id == farm_id)
            .order_by(desc(Prediction.created_at))
            .limit(limit)
        )
        return list(self.db.execute(stmt).scalars().all())

    def get_history_by_node(self, node_id: str, limit: int = 50) -> List[Prediction]:
        stmt = (
            select(Prediction)
            .where(Prediction.node_id == node_id)
            .order_by(desc(Prediction.created_at))
            .limit(limit)
        )
        return list(self.db.execute(stmt).scalars().all())
