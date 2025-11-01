"""Goal model."""

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class Goal(Base):
    """User goals model."""

    __tablename__ = "goals"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Goal info
    type = Column(String(50), nullable=False, index=True)  # weight, exercise, water, sleep, calories
    title = Column(String(255), nullable=False)
    description = Column(Text)

    # Progress
    target_value = Column(Numeric(10, 2))
    current_value = Column(Numeric(10, 2), default=0)
    unit = Column(String(20))

    # Timeline
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)

    # Status
    status = Column(
        String(20), default="active", index=True
    )  # active, completed, archived

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)

    # Relationships
    user = relationship("User", back_populates="goals")

    def __repr__(self):
        return f"<Goal {self.title} - {self.status}>"
