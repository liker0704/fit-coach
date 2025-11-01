"""Goal schemas."""

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class GoalType(str, Enum):
    """Goal type enum."""

    weight = "weight"
    exercise = "exercise"
    water = "water"
    sleep = "sleep"
    calories = "calories"


class GoalStatus(str, Enum):
    """Goal status enum."""

    active = "active"
    completed = "completed"
    archived = "archived"


class GoalBase(BaseModel):
    """Base goal schema."""

    type: GoalType
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    target_value: Decimal = Field(..., ge=0)
    current_value: Decimal = Field(default=Decimal(0), ge=0)
    unit: Optional[str] = None
    start_date: date
    end_date: Optional[date] = None
    status: GoalStatus = Field(default=GoalStatus.active)

    @field_validator("end_date")
    @classmethod
    def validate_dates(cls, v, info):
        """Validate end_date is not before start_date."""
        if v is not None and "start_date" in info.data:
            start_date = info.data["start_date"]
            if v < start_date:
                raise ValueError("end_date must be on or after start_date")
        return v


class GoalCreate(GoalBase):
    """Schema for creating a new goal."""

    pass


class GoalUpdate(BaseModel):
    """Schema for updating a goal."""

    type: Optional[GoalType] = None
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    target_value: Optional[Decimal] = Field(None, ge=0)
    current_value: Optional[Decimal] = Field(None, ge=0)
    unit: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[GoalStatus] = None

    @field_validator("end_date")
    @classmethod
    def validate_dates(cls, v, info):
        """Validate end_date is not before start_date."""
        if v is not None and "start_date" in info.data:
            start_date = info.data["start_date"]
            if start_date is not None and v < start_date:
                raise ValueError("end_date must be on or after start_date")
        return v


class GoalResponse(GoalBase):
    """Schema for goal response."""

    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
