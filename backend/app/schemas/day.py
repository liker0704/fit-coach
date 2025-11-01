"""Day schemas."""

from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class DayBase(BaseModel):
    """Base day schema."""

    date: date
    tag: Optional[str] = Field(None, max_length=50)
    feeling: Optional[int] = Field(None, ge=1, le=5)
    effort_score: Optional[Decimal] = Field(None, ge=0, le=10)
    summary: Optional[str] = None


class DayCreate(DayBase):
    """Schema for creating a new day."""

    date: date
    tag: Optional[str] = Field(None, max_length=50)
    feeling: Optional[int] = Field(None, ge=1, le=5)
    effort_score: Optional[Decimal] = Field(None, ge=0, le=10)
    summary: Optional[str] = None


class DayUpdate(BaseModel):
    """Schema for updating a day."""

    tag: Optional[str] = Field(None, max_length=50)
    feeling: Optional[int] = Field(None, ge=1, le=5)
    effort_score: Optional[Decimal] = Field(None, ge=0, le=10)
    summary: Optional[str] = None
    llm_advice: Optional[str] = None


class DayResponse(DayBase):
    """Schema for day response."""

    id: int
    user_id: int
    llm_advice: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
