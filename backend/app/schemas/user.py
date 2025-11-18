"""User schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.core.password_validator import get_password_validator


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, max_length=255)


class UserCreate(UserBase):
    """Schema for user registration."""

    password: str = Field(..., min_length=8, max_length=100)
    age: Optional[int] = Field(None, ge=10, le=120)
    height: Optional[float] = Field(None, ge=50, le=300)  # in cm
    weight: Optional[float] = Field(None, ge=20, le=500)  # in kg

    @field_validator('password')
    @classmethod
    def validate_password_complexity(cls, v: str, info) -> str:
        """Validate password complexity requirements.

        Args:
            v: Password value
            info: Validation info containing other fields

        Returns:
            Password if valid

        Raises:
            ValueError: If password doesn't meet requirements
        """
        validator = get_password_validator()

        # Get username and email from context if available
        username = info.data.get('username')
        email = info.data.get('email')

        is_valid, errors = validator.validate(v, username=username, email=email)

        if not is_valid:
            # Create detailed error message
            error_msg = "Password validation failed:\n- " + "\n- ".join(errors)
            raise ValueError(error_msg)

        return v


class UserUpdate(BaseModel):
    """Schema for user profile update (only profile fields, not auth fields)."""

    full_name: Optional[str] = Field(None, max_length=255)
    age: Optional[int] = Field(None, ge=10, le=120)
    height: Optional[float] = Field(None, ge=50, le=300)  # in cm
    weight: Optional[float] = Field(None, ge=20, le=500)  # in kg
    target_weight: Optional[float] = Field(None, ge=20, le=500)  # in kg
    language: Optional[str] = Field(None, max_length=10)
    timezone: Optional[str] = Field(None, max_length=50)
    water_goal: Optional[float] = Field(None, ge=0, le=10)  # liters
    calorie_goal: Optional[int] = Field(None, ge=0, le=10000)
    sleep_goal: Optional[float] = Field(None, ge=0, le=24)  # hours


class UserResponse(UserBase):
    """Schema for user response."""

    id: int
    username: Optional[str] = Field(None, min_length=3, max_length=50)  # Override to make optional
    age: Optional[int] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    target_weight: Optional[float] = None

    # Settings
    language: Optional[str] = "en"
    timezone: Optional[str] = "UTC"
    water_goal: Optional[float] = 2.5
    calorie_goal: Optional[int] = 2000
    sleep_goal: Optional[float] = 8.0

    # Status
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False

    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class UserInDB(UserResponse):
    """Internal schema with hashed password."""

    hashed_password: str


class ChangePasswordRequest(BaseModel):
    """Schema for password change request."""

    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, max_length=100)

    @field_validator('new_password')
    @classmethod
    def validate_password_complexity(cls, v: str) -> str:
        """Validate new password complexity requirements.

        Args:
            v: New password value

        Returns:
            Password if valid

        Raises:
            ValueError: If password doesn't meet requirements
        """
        validator = get_password_validator()
        is_valid, errors = validator.validate(v)

        if not is_valid:
            error_msg = "Password validation failed:\n- " + "\n- ".join(errors)
            raise ValueError(error_msg)

        return v
