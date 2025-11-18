"""SleepRecord model."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, Text, func
from sqlalchemy.orm import relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.day import Day


class SleepRecord(Base):
    """Sleep tracking model."""

    __tablename__ = "sleep_records"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign keys
    day_id = Column(Integer, ForeignKey("days.id", ondelete="CASCADE"), nullable=False, index=True)

    # Sleep times
    bedtime = Column(DateTime)
    wake_time = Column(DateTime)
    duration = Column(Numeric(4, 2))  # hours (calculated)

    # Sleep quality
    quality = Column(Integer)  # 1-5
    deep_sleep = Column(Numeric(4, 2))  # hours
    rem_sleep = Column(Numeric(4, 2))  # hours

    # Additional info
    interruptions = Column(Integer, default=0)
    notes = Column(Text)

    # AI
    ai_analysis = Column(Text)
    ai_recommendations = Column(Text)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    day = relationship("Day", back_populates="sleep_records")

    def __repr__(self):
        return f"<SleepRecord {self.duration}h - Day {self.day_id}>"
