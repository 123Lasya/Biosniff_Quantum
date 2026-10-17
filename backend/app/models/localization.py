from datetime import datetime, timezone
from typing import Optional, Any
from sqlalchemy import String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class LocalizationResult(Base):
    """
    Stores spatial disease localization coordinates calculated when one or more
    nodes detect disease. Coordinates are computed using authoritative node GPS
    and wind-aware relative Gaussian plume likelihood estimation.
    """
    __tablename__ = "localization_results"

    localization_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    farm_id: Mapped[int] = mapped_column(
        ForeignKey("farms.farm_id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    trigger_node_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("nodes.node_id", ondelete="CASCADE"),
        index=True,
        nullable=True
    )
    trigger_prediction_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("predictions.prediction_id", ondelete="SET NULL"),
        nullable=True
    )

    # Local metric coordinates (meters East, meters North from farm origin)
    predicted_source_x: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    predicted_source_y: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Geographic coordinates (WGS84 GPS)
    estimated_latitude: Mapped[float] = mapped_column(Float, nullable=False)
    estimated_longitude: Mapped[float] = mapped_column(Float, nullable=False)
    confidence_radius_meters: Mapped[float] = mapped_column(Float, default=25.0, nullable=False)

    # Localization / source-likelihood score (prototype likelihood score, not statistically calibrated)
    source_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # Nodes that triggered the localization
    trigger_nodes: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)

    # All unique disease conditions detected across trigger nodes (never collapsed)
    detected_conditions: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)

    # Affected zone payload: {center_x, center_y, radius_m, geojson}
    affected_zone: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)

    # Legacy polygon or GeoJSON circle representing affected crop zone
    affected_area_geojson: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)

    severity: Mapped[str] = mapped_column(String(50), default="medium", nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)  # active, contained, resolved

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

    # Property aliases for easy access
    @property
    def timestamp(self) -> datetime:
        return self.created_at

    @property
    def latitude(self) -> float:
        return self.estimated_latitude

    @property
    def longitude(self) -> float:
        return self.estimated_longitude

    @property
    def radius(self) -> float:
        return self.confidence_radius_meters

    @property
    def radius_m(self) -> float:
        return self.confidence_radius_meters

    # Relationships
    farm: Mapped["Farm"] = relationship("Farm", back_populates="localizations")
    trigger_node: Mapped["Node"] = relationship("Node")
    trigger_prediction: Mapped[Optional["Prediction"]] = relationship("Prediction")

    def __repr__(self) -> str:
        return (
            f"<LocalizationResult id={self.localization_id} farm={self.farm_id} "
            f"node='{self.trigger_node_id}' lat={self.estimated_latitude:.5f} lng={self.estimated_longitude:.5f}>"
        )
