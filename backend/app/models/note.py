"""Note model."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.day import Day


class Note(Base):
    """Personal notes model."""

    __tablename__ = "notes"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign keys
    day_id = Column(Integer, ForeignKey("days.id", ondelete="CASCADE"), nullable=False, index=True)

    # Note info
    title = Column(String(255))
    content = Column(Text, nullable=False)  # Markdown

    # Tags and attachments
    tags = Column(JSONB)
    attachments = Column(JSONB)  # URLs to files

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    day = relationship("Day", back_populates="notes")

    def __repr__(self):
        return f"<Note {self.title} - Day {self.day_id}>"
