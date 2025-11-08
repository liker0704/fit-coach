"""Training program model."""

from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class TrainingProgram(Base):
    """Training program model for storing generated 12-week training programs."""

    __tablename__ = "training_programs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(200), nullable=False)  # e.g., "12-Week Strength Program"
    description = Column(Text, nullable=True)

    # Program configuration
    goal = Column(String(100), nullable=False)  # e.g., "muscle_gain", "weight_loss"
    experience_level = Column(String(50), nullable=False)  # beginner/intermediate/advanced
    days_per_week = Column(Integer, nullable=False)
    equipment = Column(JSON, nullable=True)  # List of available equipment

    # Generated program data (JSON structure with 12 weeks)
    program_data = Column(JSON, nullable=False)

    # Summary/metadata
    summary = Column(JSON, nullable=True)  # Notes, progression strategy, etc.

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Active status (user can have multiple programs)
    is_active = Column(Integer, default=1)  # 1 = active, 0 = archived

    # Relationship
    user = relationship("User", backref="training_programs")

    def __repr__(self) -> str:
        return f"<TrainingProgram(id={self.id}, user_id={self.user_id}, name={self.name}, goal={self.goal})>"
