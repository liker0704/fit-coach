"""Day model."""

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Column, Date, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.exercise import Exercise
    from app.models.llm_summary import LLMSummary
    from app.models.meal import Meal
    from app.models.mood_record import MoodRecord
    from app.models.note import Note
    from app.models.sleep_record import SleepRecord
    from app.models.user import User
    from app.models.water_intake import WaterIntake


class Day(Base):
    """Day model - main entity for daily tracking."""

    __tablename__ = "days"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False, index=True)

    # Metrics
    tag = Column(String(50))
    feeling = Column(Integer)  # 1-5
    effort_score = Column(Numeric(3, 1))  # 0-10
    weight = Column(Numeric(5, 2))  # kg, optional daily weight measurement

    # Summary
    summary = Column(Text)
    llm_advice = Column(Text)

    # Relationships
    user = relationship("User", back_populates="days")
    meals = relationship("Meal", back_populates="day", cascade="all, delete-orphan")
    exercises = relationship("Exercise", back_populates="day", cascade="all, delete-orphan")
    water_intakes = relationship(
        "WaterIntake", back_populates="day", cascade="all, delete-orphan"
    )
    sleep_records = relationship(
        "SleepRecord", back_populates="day", cascade="all, delete-orphan"
    )
    mood_records = relationship(
        "MoodRecord", back_populates="day", cascade="all, delete-orphan"
    )
    notes = relationship("Note", back_populates="day", cascade="all, delete-orphan")
    llm_summary = relationship(
        "LLMSummary", back_populates="day", uselist=False, cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Day {self.date} - User {self.user_id}>"

    __table_args__ = (
        # Unique constraint: one day per user per date
        UniqueConstraint('user_id', 'date', name='uq_user_date'),
        {"sqlite_autoincrement": True},
    )
