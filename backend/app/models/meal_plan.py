"""Meal plan model."""

from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class MealPlan(Base):
    """Meal plan model for storing generated 7-day meal plans."""

    __tablename__ = "meal_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(200), nullable=False)  # e.g., "Weight Loss Plan - Week 1"
    description = Column(Text, nullable=True)

    # Plan configuration
    calorie_target = Column(Integer, nullable=False)
    dietary_preferences = Column(JSON, nullable=True)  # List of preferences
    allergies = Column(JSON, nullable=True)  # List of allergies

    # Generated meal plan data (JSON structure with 7 days)
    plan_data = Column(JSON, nullable=False)

    # Summary/metadata
    summary = Column(JSON, nullable=True)  # Macros, notes, etc.

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Active status (user can have multiple plans)
    is_active = Column(Integer, default=1)  # 1 = active, 0 = archived

    # Relationship
    user = relationship("User", backref="meal_plans")

    def __repr__(self) -> str:
        return f"<MealPlan(id={self.id}, user_id={self.user_id}, name={self.name})>"
