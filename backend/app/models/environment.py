from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class EnvironmentReading(Base):
    """
    Stores environmental microclimate readings (wind, ambient conditions, soil moisture).
    """
    __tablename__ = "environment_readings"

    reading_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
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
    
    wind_speed: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    wind_direction: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # e.g. "NE", "SW", "90deg"
    soil_moisture: Mapped[Optional[float]] = mapped_column(Float, nullable=True)     # %
    ambient_temp: Mapped[float] = mapped_column(Float, nullable=False)               # °C
    humidity: Mapped[float] = mapped_column(Float, nullable=False)                   # %
    pressure: Mapped[Optional[float]] = mapped_column(Float, nullable=True)          # hPa
    solar_radiation: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # W/m²
    
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        index=True,
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    farm: Mapped["Farm"] = relationship("Farm")
    node: Mapped[Optional["Node"]] = relationship("Node")

    def __repr__(self) -> str:
        return f"<EnvironmentReading id={self.reading_id} farm={self.farm_id} temp={self.ambient_temp} hum={self.humidity}>"
