from datetime import datetime, timezone
from typing import List, Optional, Any
from sqlalchemy import String, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Prediction(Base):
    """
    Stores an LSTM model inference result run on a rolling 5-hour window [C_i-4 ... C_i].
    Runs independently per node.
    """
    __tablename__ = "predictions"

    prediction_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
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
    cycle_id: Mapped[int] = mapped_column(
        ForeignKey("sensor_cycles.cycle_id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    
    # The 5 cycle IDs forming the rolling 5-hour input window
    window_cycle_ids: Mapped[List[int]] = mapped_column(JSON, nullable=False)
    
    predicted_class: Mapped[str] = mapped_column(String(100), nullable=False)  # healthy, blast, blight, brown_spot
    disease_detected: Mapped[bool] = mapped_column(Boolean, default=False, index=True, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    anomaly_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    raw_probabilities: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    all_class_probabilities: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    model_version: Mapped[str] = mapped_column(String(50), default="biosniff-attention-bilstm-v1-prototype", nullable=False)
    
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    window_start: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    window_end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    node: Mapped["Node"] = relationship("Node", back_populates="predictions")
    farm: Mapped["Farm"] = relationship("Farm", back_populates="predictions")

    def __repr__(self) -> str:
        return (
            f"<Prediction id={self.prediction_id} node='{self.node_id}' "
            f"detected={self.disease_detected} class='{self.predicted_class}' "
            f"conf={self.confidence:.2f}>"
        )
