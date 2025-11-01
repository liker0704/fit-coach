"""AI coaching and summary schemas."""

import datetime
from datetime import datetime as dt_datetime
from typing import Optional

from pydantic import BaseModel, Field


class CoachingRequest(BaseModel):
    """Request schema for coaching advice."""

    context: str = Field(
        ...,
        description="Context for coaching advice",
        examples=["morning motivation", "post-workout", "meal planning"],
    )


class CoachingResponse(BaseModel):
    """Response schema for coaching advice."""

    advice: str
    generated_at: dt_datetime

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "advice": "Great job on...",
                "generated_at": "2025-11-01T10:30:00",
            }
        }


class SummaryRequest(BaseModel):
    """Request schema for health summary."""

    period: str = Field(
        ..., description="Period for summary: 'daily', 'weekly', or 'monthly'"
    )
    date: Optional[datetime.date] = Field(
        None, description="Specific date (defaults to today)"
    )


class SummaryResponse(BaseModel):
    """Response schema for health summary."""

    summary: str
    period: str
    date_range: str
    generated_at: dt_datetime

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "summary": "This week you...",
                "period": "weekly",
                "date_range": "2025-10-25 to 2025-11-01",
                "generated_at": "2025-11-01T10:30:00",
            }
        }
