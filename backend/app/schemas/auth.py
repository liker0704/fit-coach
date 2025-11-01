"""Authentication schemas."""

from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserLogin(BaseModel):
    """Schema for user login."""

    email: EmailStr
    password: str


class Token(BaseModel):
    """Schema for token response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for token payload."""

    user_id: Optional[int] = None
    email: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request."""

    refresh_token: str


class PasswordChange(BaseModel):
    """Schema for password change."""

    old_password: str
    new_password: str = Field(..., min_length=8, max_length=100)


class PasswordReset(BaseModel):
    """Schema for password reset."""

    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation."""

    token: str
    new_password: str = Field(..., min_length=8, max_length=100)


class EmailVerificationRequest(BaseModel):
    """Schema for email verification request."""

    token: str


class EmailVerificationResponse(BaseModel):
    """Schema for email verification response."""

    message: str
    token: Optional[str] = None  # MVP only - for testing without email service
