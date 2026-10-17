from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.alert import Alert


class AlertRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        farm_id: int,
        alert_type: str,
        title: str,
        message: str,
        node_id: Optional[str] = None,
        severity: str = "warning"
    ) -> Alert:
        alert = Alert(
            farm_id=farm_id,
            node_id=node_id,
            alert_type=alert_type,
            severity=severity,
            title=title,
            message=message,
            is_read=False,
            is_acknowledged=False,
            created_at=datetime.now(timezone.utc)
        )
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        return alert

    def get_by_farm_id(self, farm_id: int, limit: int = 50) -> List[Alert]:
        return self.db.query(Alert).filter(
            Alert.farm_id == farm_id
        ).order_by(Alert.created_at.desc()).limit(limit).all()

    def get_by_node_id(self, node_id: str, limit: int = 50) -> List[Alert]:
        return self.db.query(Alert).filter(
            Alert.node_id == node_id
        ).order_by(Alert.created_at.desc()).limit(limit).all()

    def get_by_id(self, alert_id: int) -> Optional[Alert]:
        return self.db.query(Alert).filter(Alert.alert_id == alert_id).first()

    def mark_as_read(self, alert_id: int) -> Optional[Alert]:
        alert = self.get_by_id(alert_id)
        if alert:
            alert.is_read = True
            self.db.commit()
            self.db.refresh(alert)
        return alert

    def mark_all_as_read(self, farm_id: int) -> int:
        count = self.db.query(Alert).filter(
            Alert.farm_id == farm_id,
            Alert.is_read == False
        ).update({"is_read": True})
        self.db.commit()
        return count

