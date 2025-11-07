"""Agent memory model."""

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class AgentMemory(Base):
    """Agent memory model for storing user context and preferences."""

    __tablename__ = "agent_memories"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Memory classification
    agent_type = Column(String(50), nullable=False, index=True)  # nutrition, fitness, wellness
    memory_type = Column(String(20), nullable=False, index=True)  # preference, fact, action

    # Memory content
    key = Column(String(100), nullable=True)  # For preferences (e.g., "diet", "favorite_exercise")
    value = Column(Text, nullable=False)  # The actual memory content

    # Additional context
    meta_data = Column(JSONB, nullable=True)  # Extra data like severity, timestamps, etc.

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default="NOW()",
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default="NOW()",
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    user = relationship("User", back_populates="agent_memories")

    def __repr__(self):
        return f"<AgentMemory {self.agent_type}:{self.memory_type} - {self.key or 'fact'}>"
