"""MoodRecord model."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.day import Day


class MoodRecord(Base):
    """Mood tracking model."""

    __tablename__ = "mood_records"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign keys
    day_id = Column(Integer, ForeignKey("days.id", ondelete="CASCADE"), nullable=False)

    # Mood info
    time = Column(DateTime, default=datetime.utcnow, index=True)
    rating = Column(Integer, nullable=False)  # 1-5

    # Levels
    energy_level = Column(Integer)  # 1-5
    stress_level = Column(Integer)  # 1-5
    anxiety_level = Column(Integer)  # 1-5

    # Tags and notes
    tags = Column(JSONB)  # ["happy", "tired", "stressed", "focused"]
    notes = Column(Text)

    # AI
    ai_sentiment = Column(String(50))
    ai_suggestions = Column(Text)

    # Relationships
    day = relationship("Day", back_populates="mood_records")

    def __repr__(self):
        return f"<MoodRecord rating={self.rating} at {self.time}>"
