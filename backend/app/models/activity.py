from datetime import datetime, timezone
from typing import Optional, Any
from sqlalchemy import String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class ActivityLog(Base):
    """
    Audit log tracking system operations, user logins, data ingestion, and model executions.
    """
    __tablename__ = "activity_logs"

    activity_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.user_id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    farm_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("farms.farm_id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    details: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    user: Mapped[Optional["User"]] = relationship("User")
    farm: Mapped[Optional["Farm"]] = relationship("Farm")

    def __repr__(self) -> str:
        return f"<ActivityLog id={self.activity_id} action='{self.action}'>"
