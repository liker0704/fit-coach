"""Meal and MealItem models."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String, Text, Time, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.day import Day


class Meal(Base):
    """Meal model."""

    __tablename__ = "meals"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign keys
    day_id = Column(Integer, ForeignKey("days.id", ondelete="CASCADE"), nullable=False, index=True)

    # Meal info
    category = Column(String(20), nullable=False, index=True)  # breakfast, lunch, dinner, snack
    time = Column(Time)

    # Nutrition totals
    calories = Column(Numeric(7, 2))
    protein = Column(Numeric(6, 2))  # grams
    carbs = Column(Numeric(6, 2))
    fat = Column(Numeric(6, 2))
    fiber = Column(Numeric(5, 2))
    sugar = Column(Numeric(5, 2))
    sodium = Column(Numeric(7, 2))  # mg

    # Details
    notes = Column(Text)
    photo_url = Column(String(500))

    # Photo processing (Vision Agent)
    photo_path = Column(String(500))  # Local file path for uploaded photo
    photo_processing_status = Column(String(20), default="pending")  # pending/processing/completed/failed
    photo_processing_error = Column(Text)  # Error message if failed
    ai_recognized_items = Column(JSONB)  # JSON array of recognized food items

    # AI
    ai_summary = Column(Text)
    ai_suggestions = Column(Text)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    day = relationship("Day", back_populates="meals")
    items = relationship("MealItem", back_populates="meal", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Meal {self.category} - Day {self.day_id}>"


class MealItem(Base):
    """Individual food item in a meal."""

    __tablename__ = "meal_items"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign keys
    meal_id = Column(Integer, ForeignKey("meals.id", ondelete="CASCADE"), nullable=False)

    # Item info
    name = Column(String(255), nullable=False, index=True)
    amount = Column(Numeric(7, 2))
    unit = Column(String(20))  # g, ml, cup, piece
    calories = Column(Numeric(7, 2))

    # Nutrition (optional)
    protein = Column(Numeric(6, 2))
    carbs = Column(Numeric(6, 2))
    fat = Column(Numeric(6, 2))

    # Relationships
    meal = relationship("Meal", back_populates="items")

    def __repr__(self):
        return f"<MealItem {self.name} - Meal {self.meal_id}>"
