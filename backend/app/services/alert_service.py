from typing import Optional, List, Dict, Any
from enum import Enum
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.alert import Alert
from app.repositories.alert_repo import AlertRepository


class AlertType(str, Enum):
    DISEASE_ALERT = "DISEASE_ALERT"
    NODE_OFFLINE = "NODE_OFFLINE"
    NODE_NO_DATA = "NODE_NO_DATA"
    LOW_BATTERY = "LOW_BATTERY"
    CONNECTIVITY_WARNING = "CONNECTIVITY_WARNING"
    SENSOR_DATA_ERROR = "SENSOR_DATA_ERROR"


class AlertService:
    def __init__(self, db: Session):
        self.db = db
        self.alert_repo = AlertRepository(db)

    def create_alert(
        self,
        farm_id: int,
        alert_type: str,
        title: str,
        message: str,
        node_id: Optional[str] = None,
        severity: str = "warning"
    ) -> Alert:
        """
        Creates and stores an alert in the database.
        Accepts standard enum values or lowercase aliases.
        """
        # Normalize type representation
        normalized_type = alert_type.upper() if hasattr(alert_type, "upper") else str(alert_type)
        if normalized_type not in AlertType.__members__:
            # Map common variations
            mapping = {
                "CROP_DISEASE_DETECTED": AlertType.DISEASE_ALERT.value,
                "DISEASE_DETECTED": AlertType.DISEASE_ALERT.value,
                "NODE_DATA_MISSING": AlertType.NODE_NO_DATA.value,
                "MISSING_DATA": AlertType.NODE_NO_DATA.value,
                "BATTERY_LOW": AlertType.LOW_BATTERY.value,
            }
            normalized_type = mapping.get(normalized_type, AlertType.SENSOR_DATA_ERROR.value)

        # Check for duplicate unread alert within recent window
        existing = (
            self.db.query(Alert)
            .filter(
                Alert.farm_id == farm_id,
                Alert.alert_type == normalized_type,
                Alert.node_id == node_id,
                Alert.is_read == False
            )
            .first()
        )
        if existing:
            return existing

        return self.alert_repo.create(
            farm_id=farm_id,
            alert_type=normalized_type,
            title=title,
            message=message,
            node_id=node_id,
            severity=severity
        )

    def get_farm_alerts(self, farm_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        alerts = self.alert_repo.get_by_farm_id(farm_id=farm_id, limit=limit)
        return [self._format_alert(a) for a in alerts]

    def get_node_alerts(self, node_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        alerts = self.alert_repo.get_by_node_id(node_id=node_id, limit=limit)
        return [self._format_alert(a) for a in alerts]

    # Alias helpers for service-to-service compatibility
    get_alerts_for_farm = get_farm_alerts
    get_alerts_for_node = get_node_alerts

    def mark_alert_read(self, alert_id: int) -> Dict[str, Any]:
        alert = self.alert_repo.mark_as_read(alert_id)
        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Alert with id {alert_id} not found"
            )
        return self._format_alert(alert)

    mark_read = mark_alert_read

    def _format_alert(self, alert: Alert) -> Dict[str, Any]:
        return {
            "alert_id": alert.alert_id,
            "farm_id": alert.farm_id,
            "node_id": alert.node_id,
            "type": alert.alert_type,
            "alert_type": alert.alert_type,
            "severity": alert.severity,
            "title": alert.title,
            "message": alert.message,
            "is_read": alert.is_read,
            "is_acknowledged": alert.is_acknowledged,
            "created_at": alert.created_at
        }
