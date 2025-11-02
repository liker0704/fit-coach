"""Water intake schemas."""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class WaterBase(BaseModel):
    """Base water intake schema."""

    amount: Decimal = Field(..., ge=0, le=10, description="Water amount in liters")
    time: Optional[datetime] = Field(None, description="Time when water was consumed")


class WaterCreate(WaterBase):
    """Schema for creating a new water intake entry."""

    amount: Decimal = Field(..., ge=0, le=10, description="Water amount in liters")
    time: Optional[datetime] = Field(None, description="Time when water was consumed")

    @field_validator('time', mode='before')
    @classmethod
    def parse_time_string(cls, v):
        """Parse HH:MM or HH:MM:SS format time strings into datetime objects."""
        if not v or v == '':
            return None
        if isinstance(v, str):
            # Try parsing "HH:MM:SS" format first, then "HH:MM"
            for fmt in ('%H:%M:%S', '%H:%M'):
                try:
                    time_obj = datetime.strptime(v, fmt).time()
                    # Combine with today's date
                    return datetime.combine(datetime.now().date(), time_obj)
                except ValueError:
                    continue
            # If both formats fail, return as-is (let Pydantic handle validation error)
            return v
        return v


class WaterUpdate(BaseModel):
    """Schema for updating a water intake entry."""

    amount: Optional[Decimal] = Field(None, ge=0, le=10, description="Water amount in liters")
    time: Optional[datetime] = Field(None, description="Time when water was consumed")


class WaterResponse(WaterBase):
    """Schema for water intake response."""

    id: int
    day_id: int

    model_config = ConfigDict(from_attributes=True)
