from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Node(Base):
    __tablename__ = "nodes"

    # Hardware Node Identifier (e.g. 'node_1', 'NODE-01', 'ESP32-MASTER-01')
    node_id: Mapped[str] = mapped_column(String(50), primary_key=True, index=True)
    farm_id: Mapped[int] = mapped_column(
        ForeignKey("farms.farm_id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    node_name: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Authoritative GPS coordinates stored in database (DO NOT HARDCODE)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    
    status: Mapped[str] = mapped_column(String(50), default="online", nullable=False)  # online, offline, warning, error
    battery_percentage: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)
    signal_strength: Mapped[float] = mapped_column(Float, default=-65.0, nullable=False)  # RSSI in dBm
    firmware_version: Mapped[str] = mapped_column(String(50), default="v1.2.4-mesh", nullable=False)
    is_master: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    last_seen: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    farm: Mapped["Farm"] = relationship("Farm", back_populates="nodes")
    sensor_cycles: Mapped[List["SensorCycle"]] = relationship(
        "SensorCycle",
        back_populates="node",
        cascade="all, delete-orphan",
        order_by="SensorCycle.cycle_timestamp.desc()"
    )
    predictions: Mapped[List["Prediction"]] = relationship(
        "Prediction",
        back_populates="node",
        cascade="all, delete-orphan"
    )
    alerts: Mapped[List["Alert"]] = relationship(
        "Alert",
        back_populates="node",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Node id='{self.node_id}' name='{self.node_name}' farm_id={self.farm_id} status='{self.status}'>"
