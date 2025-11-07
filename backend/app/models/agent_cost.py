"""Agent cost tracking model."""

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class AgentCost(Base):
    """Agent cost tracking model for LLM API usage."""

    __tablename__ = "agent_costs"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Cost tracking fields
    agent_type = Column(String(50), nullable=False)  # nutrition, chatbot, exercise, etc.
    model = Column(String(50), nullable=False)  # gpt-4-turbo, gemini-pro, etc.
    tokens_input = Column(Integer, nullable=False)
    tokens_output = Column(Integer, nullable=False)
    cost_usd = Column(Numeric(10, 6), nullable=True)  # Cost in USD

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", backref="agent_costs")

    def __repr__(self):
        return f"<AgentCost {self.agent_type} - {self.model} - ${self.cost_usd}>"
