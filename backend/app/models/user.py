"""User model."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, DateTime, Integer, Numeric, String
from sqlalchemy.orm import relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.day import Day
    from app.models.goal import Goal
    from app.models.notification import Notification
    from app.models.refresh_token import RefreshToken


class User(Base):
    """User model."""

    __tablename__ = "users"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Authentication
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))

    # Profile
    age = Column(Integer)
    height = Column(Numeric(5, 2))  # cm
    weight = Column(Numeric(5, 2))  # kg
    target_weight = Column(Numeric(5, 2))

    # Settings
    language = Column(String(10), default="en")
    timezone = Column(String(50), default="UTC")
    water_goal = Column(Numeric(3, 1), default=2.5)  # liters
    calorie_goal = Column(Integer, default=2000)
    sleep_goal = Column(Numeric(3, 1), default=8.0)  # hours

    # Status
    is_active = Column(Boolean, default=True, index=True)
    is_superuser = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    last_login = Column(DateTime)

    # Relationships
    days = relationship("Day", back_populates="user", cascade="all, delete-orphan")
    goals = relationship("Goal", back_populates="user", cascade="all, delete-orphan")
    refresh_tokens = relationship(
        "RefreshToken", back_populates="user", cascade="all, delete-orphan"
    )
    notifications = relationship(
        "Notification", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User {self.email}>"
