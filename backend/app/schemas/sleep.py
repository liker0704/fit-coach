"""Sleep schemas."""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class SleepBase(BaseModel):
    """Base sleep schema."""

    bedtime: Optional[datetime] = None
    wake_time: Optional[datetime] = None
    duration: Optional[Decimal] = Field(None, ge=0)
    quality: Optional[int] = Field(None, ge=1, le=5)
    deep_sleep: Optional[Decimal] = Field(None, ge=0)
    rem_sleep: Optional[Decimal] = Field(None, ge=0)
    interruptions: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = None


class SleepCreate(SleepBase):
    """Schema for creating a new sleep record."""

    day_id: int


class SleepUpdate(BaseModel):
    """Schema for updating a sleep record."""

    bedtime: Optional[datetime] = None
    wake_time: Optional[datetime] = None
    duration: Optional[Decimal] = Field(None, ge=0)
    quality: Optional[int] = Field(None, ge=1, le=5)
    deep_sleep: Optional[Decimal] = Field(None, ge=0)
    rem_sleep: Optional[Decimal] = Field(None, ge=0)
    interruptions: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = None
    ai_analysis: Optional[str] = None
    ai_recommendations: Optional[str] = None


class SleepResponse(SleepBase):
    """Schema for sleep response."""

    id: int
    day_id: int
    ai_analysis: Optional[str] = None
    ai_recommendations: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
