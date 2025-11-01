"""Meal schemas."""

from datetime import datetime, time
from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class MealCategory(str, Enum):
    """Meal category enum."""

    breakfast = "breakfast"
    lunch = "lunch"
    dinner = "dinner"
    snack = "snack"


class MealBase(BaseModel):
    """Base meal schema."""

    category: MealCategory
    time: Optional[time] = None
    calories: Optional[Decimal] = Field(None, ge=0)
    protein: Optional[Decimal] = Field(None, ge=0)
    carbs: Optional[Decimal] = Field(None, ge=0)
    fat: Optional[Decimal] = Field(None, ge=0)
    fiber: Optional[Decimal] = Field(None, ge=0)
    sugar: Optional[Decimal] = Field(None, ge=0)
    sodium: Optional[Decimal] = Field(None, ge=0)
    notes: Optional[str] = None
    photo_url: Optional[str] = Field(None, max_length=500)


class MealCreate(MealBase):
    """Schema for creating a new meal."""

    category: MealCategory
    day_id: int


class MealUpdate(BaseModel):
    """Schema for updating a meal."""

    category: Optional[MealCategory] = None
    time: Optional[time] = None
    calories: Optional[Decimal] = Field(None, ge=0)
    protein: Optional[Decimal] = Field(None, ge=0)
    carbs: Optional[Decimal] = Field(None, ge=0)
    fat: Optional[Decimal] = Field(None, ge=0)
    fiber: Optional[Decimal] = Field(None, ge=0)
    sugar: Optional[Decimal] = Field(None, ge=0)
    sodium: Optional[Decimal] = Field(None, ge=0)
    notes: Optional[str] = None
    photo_url: Optional[str] = Field(None, max_length=500)
    ai_summary: Optional[str] = None
    ai_suggestions: Optional[str] = None


class MealResponse(MealBase):
    """Schema for meal response."""

    id: int
    day_id: int
    ai_summary: Optional[str] = None
    ai_suggestions: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
