from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Float, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class ConnectivityLog(Base):
    """
    Stores 5G cellular uplink and local Sub-GHz mesh connectivity telemetry.
    """
    __tablename__ = "connectivity_logs"

    log_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
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
    
    gateway_type: Mapped[str] = mapped_column(String(50), default="5G", nullable=False)
    carrier: Mapped[str] = mapped_column(String(50), default="Jio", nullable=False)
    rssi: Mapped[int] = mapped_column(Integer, default=-78, nullable=False)          # dBm
    rsrp: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)             # dBm
    rsrq: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)             # dB
    sinr: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)             # dB
    latency_ms: Mapped[float] = mapped_column(Float, default=22.0, nullable=False)
    packet_loss_pct: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="connected", nullable=False)
    
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    farm: Mapped["Farm"] = relationship("Farm")
    node: Mapped[Optional["Node"]] = relationship("Node")

    def __repr__(self) -> str:
        return f"<ConnectivityLog id={self.log_id} type='{self.gateway_type}' rssi={self.rssi} latency={self.latency_ms}ms>"
