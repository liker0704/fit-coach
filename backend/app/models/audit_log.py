"""Audit log model for tracking security-relevant events."""

from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, Column, DateTime, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class AuditLog(Base):
    """Audit log model for security events."""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    event_type = Column(String(100), nullable=False, index=True)  # e.g., "login", "logout", "password_reset"
    event_category = Column(String(50), nullable=False, index=True)  # e.g., "auth", "profile", "data"
    description = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(String(500), nullable=True)
    metadata = Column(JSON, nullable=True)  # Additional context data
    status = Column(String(20), nullable=False)  # "success" or "failure"
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationship
    user = relationship("User", backref="audit_logs")

    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, user_id={self.user_id}, event_type={self.event_type}, status={self.status})>"
