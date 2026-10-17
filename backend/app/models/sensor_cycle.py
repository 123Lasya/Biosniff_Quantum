from datetime import datetime, timezone
from typing import List, Optional, Any
from sqlalchemy import String, Float, Integer, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class SensorCycle(Base):
    """
    Represents one hourly sensing cycle for a single node.
    Per Bio-Sniff specifications, each valid hourly cycle contains:
    - exactly 10 gas-resistance readings (stored in gas_readings JSON array)
    - one temperature value (°C)
    - one humidity value (%)
    - one pressure value (hPa)
    """
    __tablename__ = "sensor_cycles"

    cycle_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    node_id: Mapped[str] = mapped_column(
        ForeignKey("nodes.node_id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    farm_id: Mapped[int] = mapped_column(
        ForeignKey("farms.farm_id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    
    cycle_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        index=True,
        nullable=False
    )
    cycle_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    # Exactly 10 gas-resistance sensor readings [R1, R2, ..., R10]
    gas_readings: Mapped[List[float]] = mapped_column(JSON, nullable=False)
    
    # Core environmental parameters
    temperature: Mapped[float] = mapped_column(Float, nullable=False)
    humidity: Mapped[float] = mapped_column(Float, nullable=False)
    pressure: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Hardware metrics
    battery: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    signal: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Data validation flag (ensures valid 10 gas readings and realistic temp/hum/pressure)
    is_valid: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    raw_payload: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    node: Mapped["Node"] = relationship("Node", back_populates="sensor_cycles")
    farm: Mapped["Farm"] = relationship("Farm", back_populates="sensor_cycles")

    def __repr__(self) -> str:
        return (
            f"<SensorCycle id={self.cycle_id} node='{self.node_id}' "
            f"cycle_no={self.cycle_number} valid={self.is_valid}>"
        )
