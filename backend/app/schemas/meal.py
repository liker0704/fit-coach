"""Meal schemas."""

from datetime import datetime, time
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional

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
    photo_path: Optional[str] = None
    photo_processing_status: Optional[str] = None
    photo_processing_error: Optional[str] = None
    ai_recognized_items: Optional[List[Dict[str, Any]]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PhotoUploadResponse(BaseModel):
    """Response after uploading meal photo."""

    meal_id: int
    status: str = "processing"  # processing/completed/failed
    message: str
    photo_path: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class MealProcessingStatus(BaseModel):
    """Status of meal photo processing."""

    meal_id: int
    status: str  # pending/processing/completed/failed
    error: Optional[str] = None
    recognized_items: Optional[List[Dict[str, Any]]] = None
    meal_data: Optional[MealResponse] = None

    model_config = ConfigDict(from_attributes=True)
