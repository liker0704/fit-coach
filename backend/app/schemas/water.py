"""Water intake schemas."""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class WaterBase(BaseModel):
    """Base water intake schema."""

    amount: Decimal = Field(..., ge=0, le=10, description="Water amount in liters")
    time: Optional[datetime] = Field(None, description="Time when water was consumed")


class WaterCreate(WaterBase):
    """Schema for creating a new water intake entry."""

    amount: Decimal = Field(..., ge=0, le=10, description="Water amount in liters")
    time: Optional[datetime] = Field(None, description="Time when water was consumed")


class WaterUpdate(BaseModel):
    """Schema for updating a water intake entry."""

    amount: Optional[Decimal] = Field(None, ge=0, le=10, description="Water amount in liters")
    time: Optional[datetime] = Field(None, description="Time when water was consumed")


class WaterResponse(WaterBase):
    """Schema for water intake response."""

    id: int
    day_id: int

    model_config = ConfigDict(from_attributes=True)
