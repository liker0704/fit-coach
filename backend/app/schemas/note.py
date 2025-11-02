"""Note schemas."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class NoteBase(BaseModel):
    """Base note schema."""

    title: Optional[str] = Field(None, max_length=255)
    content: str
    tags: Optional[List[str]] = None
    attachments: Optional[List[str]] = None


class NoteCreate(NoteBase):
    """Schema for creating a new note."""

    pass


class NoteUpdate(BaseModel):
    """Schema for updating a note."""

    title: Optional[str] = Field(None, max_length=255)
    content: Optional[str] = None
    tags: Optional[List[str]] = None
    attachments: Optional[List[str]] = None


class NoteResponse(NoteBase):
    """Schema for note response."""

    id: int
    day_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
