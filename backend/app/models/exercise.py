"""Exercise and ExerciseSet models."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.day import Day


class Exercise(Base):
    """Exercise session model."""

    __tablename__ = "exercises"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign keys
    day_id = Column(Integer, ForeignKey("days.id", ondelete="CASCADE"), nullable=False, index=True)

    # Exercise info
    type = Column(String(50), nullable=False, index=True)  # running, gym, yoga, cycling
    name = Column(String(255))

    # Time
    start_time = Column(DateTime)
    duration = Column(Integer)  # minutes

    # Metrics
    distance = Column(Numeric(6, 2))  # km
    calories_burned = Column(Numeric(7, 2))
    heart_rate_avg = Column(Integer)
    heart_rate_max = Column(Integer)
    intensity = Column(Integer)  # 1-5

    # Details
    notes = Column(Text)

    # AI
    ai_feedback = Column(Text)
    ai_recommendations = Column(Text)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    day = relationship("Day", back_populates="exercises")
    sets = relationship("ExerciseSet", back_populates="exercise", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Exercise {self.type} - Day {self.day_id}>"


class ExerciseSet(Base):
    """Individual set in a workout."""

    __tablename__ = "exercise_sets"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign keys
    exercise_id = Column(
        Integer, ForeignKey("exercises.id", ondelete="CASCADE"), nullable=False
    )

    # Set info
    set_number = Column(Integer, nullable=False)
    exercise_name = Column(String(255))
    reps = Column(Integer)
    weight = Column(Numeric(5, 2))  # kg
    rest_seconds = Column(Integer)

    # Relationships
    exercise = relationship("Exercise", back_populates="sets")

    def __repr__(self):
        return f"<ExerciseSet {self.exercise_name} Set {self.set_number}>"
