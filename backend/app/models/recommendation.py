from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Recommendation(Base):
    """
    Stores actionable agronomic guidance and interventions triggered by disease detection.
    """
    __tablename__ = "recommendations"

    recommendation_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    farm_id: Mapped[int] = mapped_column(
        ForeignKey("farms.farm_id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    prediction_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("predictions.prediction_id", ondelete="SET NULL"),
        nullable=True
    )
    
    disease_name: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    action_type: Mapped[str] = mapped_column(String(100), default="treatment", nullable=False)
    details: Mapped[str] = mapped_column(Text, nullable=False)
    dosage: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    urgency: Mapped[str] = mapped_column(String(50), default="immediate", nullable=False)  # immediate, within_24h, preventive
    is_applied: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Property aliases for Part 4 specification compatibility
    @property
    def disease_type(self) -> str:
        return self.disease_name

    @property
    def recommendation_text(self) -> str:
        return self.details

    @property
    def priority(self) -> str:
        return self.urgency

    # Relationships
    farm: Mapped["Farm"] = relationship("Farm", back_populates="recommendations")
    prediction: Mapped[Optional["Prediction"]] = relationship("Prediction")

    def __repr__(self) -> str:
        return f"<Recommendation id={self.recommendation_id} disease='{self.disease_name}' urgency='{self.urgency}'>"
