from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Farm(Base):
    __tablename__ = "farms"

    farm_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    farmer_id: Mapped[int] = mapped_column(
        ForeignKey("farmers.farmer_id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    farm_name: Mapped[str] = mapped_column(String(150), nullable=False)
    area: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)  # in acres/hectares
    crop: Mapped[str] = mapped_column(String(100), nullable=False, default="Rice (Paddy)")
    crop_variety: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    growth_stage: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, default="Vegetative")
    address: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    boundary_geojson: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)

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
    farmer: Mapped["Farmer"] = relationship("Farmer", back_populates="farms")
    nodes: Mapped[List["Node"]] = relationship(
        "Node",
        back_populates="farm",
        cascade="all, delete-orphan",
        order_by="Node.node_id.asc()"
    )
    sensor_cycles: Mapped[List["SensorCycle"]] = relationship(
        "SensorCycle",
        back_populates="farm",
        cascade="all, delete-orphan"
    )
    predictions: Mapped[List["Prediction"]] = relationship(
        "Prediction",
        back_populates="farm",
        cascade="all, delete-orphan"
    )
    localizations: Mapped[List["LocalizationResult"]] = relationship(
        "LocalizationResult",
        back_populates="farm",
        cascade="all, delete-orphan"
    )
    alerts: Mapped[List["Alert"]] = relationship(
        "Alert",
        back_populates="farm",
        cascade="all, delete-orphan"
    )
    recommendations: Mapped[List["Recommendation"]] = relationship(
        "Recommendation",
        back_populates="farm",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Farm id={self.farm_id} name='{self.farm_name}' status='{self.status}'>"
