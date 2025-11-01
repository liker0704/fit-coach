"""Notification schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class NotificationBase(BaseModel):
    """Base notification schema."""

    type: str
    title: str = Field(..., max_length=255)
    message: Optional[str] = None
    data: Optional[dict] = None


class NotificationCreate(NotificationBase):
    """Schema for creating a new notification."""

    pass


class NotificationUpdate(BaseModel):
    """Schema for updating a notification."""

    is_read: Optional[bool] = None


class NotificationResponse(NotificationBase):
    """Schema for notification response."""

    id: int
    user_id: int
    is_read: bool
    read_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
