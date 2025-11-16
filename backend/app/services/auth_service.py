"""Authentication service."""

import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple

from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
)
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.schemas.auth import Token
from app.schemas.user import UserCreate

# In-memory token storage (MVP - use database in production)
_reset_tokens = {}  # {token: {"user_id": int, "expires_at": datetime}}
_verification_tokens = {}  # {token: {"user_id": int, "expires_at": datetime}}


class AuthService:
    """Service for authentication operations."""

    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """Create a new user.

        Args:
            db: Database session
            user_data: User creation data

        Returns:
            Created user

        Raises:
            ValueError: If user already exists
        """
        # Check if user exists
        existing_user = (
            db.query(User)
            .filter(
                (User.email == user_data.email)
                | (User.username == user_data.username)
            )
            .first()
        )

        if existing_user:
            if existing_user.email == user_data.email:
                raise ValueError("User with this email already exists")
            if existing_user.username == user_data.username:
                raise ValueError("User with this username already exists")

        # Create new user
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            age=user_data.age,
            height=user_data.height,
            weight=user_data.weight,
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        # Create email verification token
        # Note: In production, this should trigger an email send
        verification_token = AuthService.create_email_verification_token(db, db_user.id)
        # TODO: Send verification_token via email to user

        return db_user

    @staticmethod
    def authenticate_user(
        db: Session, email: str, password: str
    ) -> Optional[User]:
        """Authenticate a user.

        Args:
            db: Database session
            email: User email
            password: User password

        Returns:
            Authenticated user or None if authentication failed
        """
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    def create_tokens(db: Session, user: User) -> Token:
        """Create access and refresh tokens for user.

        Args:
            db: Database session
            user: User to create tokens for

        Returns:
            Token response with access and refresh tokens
        """
        # Create access token
        access_token = create_access_token(data={"sub": str(user.id)})

        # Create refresh token
        refresh_token = create_refresh_token(data={"sub": str(user.id)})

        # Save refresh token to database
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        db_refresh_token = RefreshToken(
            user_id=user.id,
            token=refresh_token,
            expires_at=expires_at,
        )
        db.add(db_refresh_token)
        db.commit()

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )

    @staticmethod
    def refresh_access_token(db: Session, refresh_token: str) -> Optional[str]:
        """Refresh access token using refresh token.

        Args:
            db: Database session
            refresh_token: Refresh token

        Returns:
            New access token or None if refresh token is invalid
        """
        # Verify refresh token exists and is not expired
        db_token = (
            db.query(RefreshToken)
            .filter(RefreshToken.token == refresh_token)
            .first()
        )

        if not db_token:
            return None

        if db_token.expires_at < datetime.now(timezone.utc):
            # Token expired, delete it
            db.delete(db_token)
            db.commit()
            return None

        # Create new access token
        access_token = create_access_token(data={"sub": str(db_token.user_id)})
        return access_token

    @staticmethod
    def revoke_refresh_token(db: Session, refresh_token: str) -> bool:
        """Revoke a refresh token.

        Args:
            db: Database session
            refresh_token: Refresh token to revoke

        Returns:
            True if token was revoked, False if not found
        """
        db_token = (
            db.query(RefreshToken)
            .filter(RefreshToken.token == refresh_token)
            .first()
        )

        if not db_token:
            return False

        db.delete(db_token)
        db.commit()
        return True

    @staticmethod
    def revoke_all_user_tokens(db: Session, user_id: int) -> int:
        """Revoke all refresh tokens for a user.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            Number of tokens revoked
        """
        count = (
            db.query(RefreshToken)
            .filter(RefreshToken.user_id == user_id)
            .delete()
        )
        db.commit()
        return count

    @staticmethod
    def change_password(
        db: Session, user: User, current_password: str, new_password: str
    ) -> bool:
        """Change user password.

        Args:
            db: Database session
            user: User to change password for
            current_password: Current password for verification
            new_password: New password to set

        Returns:
            True on success

        Raises:
            ValueError: If current password is incorrect
        """
        # Verify current password
        if not verify_password(current_password, user.hashed_password):
            raise ValueError("Current password is incorrect")

        # Hash and update new password
        user.hashed_password = get_password_hash(new_password)
        db.commit()
        db.refresh(user)
        return True

    @staticmethod
    def create_password_reset_token(db: Session, email: str) -> Optional[str]:
        """Create a password reset token for the user with the given email.

        Args:
            db: Database session
            email: User email address

        Returns:
            Reset token if user exists, None otherwise
        """
        # Find user by email
        user = db.query(User).filter(User.email == email).first()

        # Return None if user not found (don't reveal user existence)
        if not user:
            return None

        # Generate secure token
        token = secrets.token_urlsafe(32)

        # Store token with expiration (15 minutes)
        _reset_tokens[token] = {
            "user_id": user.id,
            "expires_at": datetime.now(timezone.utc) + timedelta(minutes=15)
        }

        return token

    @staticmethod
    def reset_password_with_token(
        db: Session, token: str, new_password: str
    ) -> Optional[User]:
        """Reset user password using a reset token.

        Args:
            db: Database session
            token: Password reset token
            new_password: New password to set

        Returns:
            User object if password was reset successfully, None if token is invalid/expired
        """
        # Check if token exists
        if token not in _reset_tokens:
            return None

        token_data = _reset_tokens[token]

        # Check if token is expired
        if token_data["expires_at"] < datetime.now(timezone.utc):
            # Remove expired token
            del _reset_tokens[token]
            return None

        # Get user
        user = db.query(User).filter(User.id == token_data["user_id"]).first()
        if not user:
            # Remove token if user doesn't exist
            del _reset_tokens[token]
            return None

        # Update password
        user.hashed_password = get_password_hash(new_password)
        db.commit()

        # Delete token (single use)
        del _reset_tokens[token]

        return user

    @staticmethod
    def create_email_verification_token(db: Session, user_id: int) -> str:
        """Create an email verification token for the user.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            Verification token
        """
        # Generate secure token
        token = secrets.token_urlsafe(32)

        # Store token with expiration (24 hours)
        _verification_tokens[token] = {
            "user_id": user_id,
            "expires_at": datetime.now(timezone.utc) + timedelta(hours=24)
        }

        return token

    @staticmethod
    def verify_email_with_token(db: Session, token: str) -> bool:
        """Verify user email using a verification token.

        Args:
            db: Database session
            token: Email verification token

        Returns:
            True if email was verified successfully, False if token is invalid/expired
        """
        # Check if token exists
        if token not in _verification_tokens:
            return False

        token_data = _verification_tokens[token]

        # Check if token is expired
        if token_data["expires_at"] < datetime.now(timezone.utc):
            # Remove expired token
            del _verification_tokens[token]
            return False

        # Get user
        user = db.query(User).filter(User.id == token_data["user_id"]).first()
        if not user:
            # Remove token if user doesn't exist
            del _verification_tokens[token]
            return False

        # Check if already verified
        if user.is_verified:
            # Remove token and return False (already verified)
            del _verification_tokens[token]
            return False

        # Mark email as verified
        user.is_verified = True
        db.commit()

        # Delete token (single use)
        del _verification_tokens[token]

        return True

    @staticmethod
    def resend_verification_email(db: Session, user_id: int) -> Optional[str]:
        """Resend verification email to user.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            Verification token if user exists and is not verified, None otherwise
        """
        # Get user
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        # Don't allow re-verification if already verified
        if user.is_verified:
            return None

        # Create and return new verification token
        return AuthService.create_email_verification_token(db, user_id)
