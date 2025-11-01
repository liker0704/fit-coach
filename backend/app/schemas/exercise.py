"""Exercise schemas."""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ExerciseBase(BaseModel):
    """Base exercise schema."""

    type: str = Field(..., max_length=50)
    name: Optional[str] = Field(None, max_length=255)
    start_time: Optional[datetime] = None
    duration: Optional[int] = Field(None, ge=0)
    distance: Optional[Decimal] = Field(None, ge=0)
    calories_burned: Optional[Decimal] = Field(None, ge=0)
    heart_rate_avg: Optional[int] = Field(None, ge=0)
    heart_rate_max: Optional[int] = Field(None, ge=0)
    intensity: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = None


class ExerciseCreate(ExerciseBase):
    """Schema for creating a new exercise."""

    type: str = Field(..., max_length=50)
    name: Optional[str] = Field(None, max_length=255)
    start_time: Optional[datetime] = None
    duration: Optional[int] = Field(None, ge=0)
    distance: Optional[Decimal] = Field(None, ge=0)
    calories_burned: Optional[Decimal] = Field(None, ge=0)
    heart_rate_avg: Optional[int] = Field(None, ge=0)
    heart_rate_max: Optional[int] = Field(None, ge=0)
    intensity: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = None


class ExerciseUpdate(BaseModel):
    """Schema for updating an exercise."""

    type: Optional[str] = Field(None, max_length=50)
    name: Optional[str] = Field(None, max_length=255)
    start_time: Optional[datetime] = None
    duration: Optional[int] = Field(None, ge=0)
    distance: Optional[Decimal] = Field(None, ge=0)
    calories_burned: Optional[Decimal] = Field(None, ge=0)
    heart_rate_avg: Optional[int] = Field(None, ge=0)
    heart_rate_max: Optional[int] = Field(None, ge=0)
    intensity: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = None
    ai_feedback: Optional[str] = None
    ai_recommendations: Optional[str] = None


class ExerciseResponse(ExerciseBase):
    """Schema for exercise response."""

    id: int
    day_id: int
    ai_feedback: Optional[str] = None
    ai_recommendations: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
