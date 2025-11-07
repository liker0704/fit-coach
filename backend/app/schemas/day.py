"""Day schemas."""

from datetime import date
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.meal import MealResponse
from app.schemas.exercise import ExerciseResponse
from app.schemas.water import WaterResponse
from app.schemas.sleep import SleepResponse
from app.schemas.mood import MoodResponse
from app.schemas.note import NoteResponse


class DayBase(BaseModel):
    """Base day schema."""

    date: date
    tag: Optional[str] = Field(None, max_length=50)
    feeling: Optional[int] = Field(None, ge=1, le=5)
    effort_score: Optional[Decimal] = Field(None, ge=0, le=10)
    weight: Optional[Decimal] = Field(None, gt=0, le=500)
    summary: Optional[str] = None


class DayCreate(DayBase):
    """Schema for creating a new day."""

    date: date
    tag: Optional[str] = Field(None, max_length=50)
    feeling: Optional[int] = Field(None, ge=1, le=5)
    effort_score: Optional[Decimal] = Field(None, ge=0, le=10)
    weight: Optional[Decimal] = Field(None, gt=0, le=500)
    summary: Optional[str] = None


class DayUpdate(BaseModel):
    """Schema for updating a day."""

    tag: Optional[str] = Field(None, max_length=50)
    feeling: Optional[int] = Field(None, ge=1, le=5)
    effort_score: Optional[Decimal] = Field(None, ge=0, le=10)
    weight: Optional[Decimal] = Field(None, gt=0, le=500)
    summary: Optional[str] = None
    llm_advice: Optional[str] = None


class DayResponse(DayBase):
    """Schema for day response."""

    id: int
    user_id: int
    llm_advice: Optional[str] = None
    meals: List[MealResponse] = Field(default_factory=list)
    exercises: List[ExerciseResponse] = Field(default_factory=list)
    water_intakes: List[WaterResponse] = Field(default_factory=list)
    sleep_records: List[SleepResponse] = Field(default_factory=list)
    mood_records: List[MoodResponse] = Field(default_factory=list)
    notes: List[NoteResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
