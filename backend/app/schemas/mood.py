"""Mood schemas."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class MoodBase(BaseModel):
    """Base mood schema."""

    time: datetime
    rating: int = Field(ge=1, le=5)
    energy_level: Optional[int] = Field(None, ge=1, le=5)
    stress_level: Optional[int] = Field(None, ge=1, le=5)
    anxiety_level: Optional[int] = Field(None, ge=1, le=5)
    tags: Optional[List[str]] = None
    notes: Optional[str] = None


class MoodCreate(MoodBase):
    """Schema for creating a new mood record."""

    pass


class MoodUpdate(BaseModel):
    """Schema for updating a mood record."""

    time: Optional[datetime] = None
    rating: Optional[int] = Field(None, ge=1, le=5)
    energy_level: Optional[int] = Field(None, ge=1, le=5)
    stress_level: Optional[int] = Field(None, ge=1, le=5)
    anxiety_level: Optional[int] = Field(None, ge=1, le=5)
    tags: Optional[List[str]] = None
    notes: Optional[str] = None
    ai_sentiment: Optional[str] = None
    ai_suggestions: Optional[str] = None


class MoodResponse(MoodBase):
    """Schema for mood response."""

    id: int
    day_id: int
    ai_sentiment: Optional[str] = None
    ai_suggestions: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
