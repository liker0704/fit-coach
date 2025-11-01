"""Notification model."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class Notification(Base):
    """User notifications model."""

    __tablename__ = "notifications"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Notification info
    type = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text)

    # Additional data
    data = Column(JSONB)

    # Status
    is_read = Column(Boolean, default=False, index=True)
    read_at = Column(DateTime)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = relationship("User", back_populates="notifications")

    def __repr__(self):
        return f"<Notification {self.title} - User {self.user_id}>"
