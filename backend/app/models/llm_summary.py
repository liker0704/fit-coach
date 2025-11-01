"""LLMSummary model."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.day import Day


class LLMSummary(Base):
    """AI-generated daily summary model."""

    __tablename__ = "llm_summaries"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign keys (one-to-one with Day)
    day_id = Column(
        Integer, ForeignKey("days.id", ondelete="CASCADE"), nullable=False, unique=True
    )

    # Main summary
    summary_text = Column(Text, nullable=False)
    effort_score = Column(Numeric(3, 1), nullable=False)  # 0-10
    score_reason = Column(Text)

    # Detailed analysis
    nutrition_analysis = Column(Text)
    exercise_analysis = Column(Text)
    sleep_analysis = Column(Text)
    mood_analysis = Column(Text)

    # Recommendations
    tomorrow_advice = Column(Text)
    weekly_goals = Column(JSONB)

    # Meta
    model_used = Column(String(50))
    prompt_version = Column(String(20))
    tokens_used = Column(Integer)
    generation_time = Column(Numeric(6, 2))  # seconds

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    day = relationship("Day", back_populates="llm_summary")

    def __repr__(self):
        return f"<LLMSummary score={self.effort_score} - Day {self.day_id}>"
