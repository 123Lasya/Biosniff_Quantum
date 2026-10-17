from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Alert(Base):
    """
    Stores system, disease, and node-health alerts.
    Includes no-data alerts when a node fails to report a cycle.
    """
    __tablename__ = "alerts"

    alert_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    farm_id: Mapped[int] = mapped_column(
        ForeignKey("farms.farm_id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    node_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("nodes.node_id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # disease_detected, node_data_missing, low_battery, offline, environmental_risk
    alert_type: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    severity: Mapped[str] = mapped_column(String(20), default="warning", nullable=False)  # info, warning, critical
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_acknowledged: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    farm: Mapped["Farm"] = relationship("Farm", back_populates="alerts")
    node: Mapped[Optional["Node"]] = relationship("Node", back_populates="alerts")

    def __repr__(self) -> str:
        return f"<Alert id={self.alert_id} type='{self.alert_type}' severity='{self.severity}'>"
