from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.localization import LocalizationResult


class LocalizationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        farm_id: int,
        predicted_source_x: float,
        predicted_source_y: float,
        estimated_latitude: float,
        estimated_longitude: float,
        confidence_radius_meters: float,
        source_score: float,
        trigger_nodes: List[str],
        detected_conditions: List[str],
        affected_zone: Optional[Dict[str, Any]] = None,
        trigger_node_id: Optional[str] = None,
        trigger_prediction_id: Optional[int] = None,
        severity: str = "warning",
        status: str = "active"
    ) -> LocalizationResult:
        now = datetime.now(timezone.utc)
        record = LocalizationResult(
            farm_id=farm_id,
            trigger_node_id=trigger_node_id or (trigger_nodes[0] if trigger_nodes else None),
            trigger_prediction_id=trigger_prediction_id,
            predicted_source_x=round(predicted_source_x, 2),
            predicted_source_y=round(predicted_source_y, 2),
            estimated_latitude=estimated_latitude,
            estimated_longitude=estimated_longitude,
            confidence_radius_meters=round(confidence_radius_meters, 2),
            source_score=round(source_score, 4),
            trigger_nodes=trigger_nodes,
            detected_conditions=detected_conditions,
            affected_zone=affected_zone or {
                "center_x": round(predicted_source_x, 2),
                "center_y": round(predicted_source_y, 2),
                "radius_m": round(confidence_radius_meters, 2)
            },
            affected_area_geojson={
                "type": "Point",
                "coordinates": [estimated_longitude, estimated_latitude],
                "properties": {
                    "radius_meters": round(confidence_radius_meters, 2),
                    "source_score": round(source_score, 4)
                }
            },
            severity=severity,
            status=status,
            created_at=now,
            updated_at=now
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_latest_for_farm(self, farm_id: int) -> Optional[LocalizationResult]:
        return self.db.query(LocalizationResult).filter(
            LocalizationResult.farm_id == farm_id
        ).order_by(LocalizationResult.created_at.desc()).first()

    def get_latest_by_farm(self, farm_id: int) -> Optional[LocalizationResult]:
        return self.get_latest_for_farm(farm_id)

    def get_history_for_farm(self, farm_id: int, limit: int = 50) -> List[LocalizationResult]:
        return self.db.query(LocalizationResult).filter(
            LocalizationResult.farm_id == farm_id
        ).order_by(LocalizationResult.created_at.desc()).limit(limit).all()

    def get_history_by_farm(self, farm_id: int, limit: int = 50) -> List[LocalizationResult]:
        return self.get_history_for_farm(farm_id, limit=limit)

    def get_by_id(self, localization_id: int) -> Optional[LocalizationResult]:
        return self.db.query(LocalizationResult).filter(
            LocalizationResult.localization_id == localization_id
        ).first()
