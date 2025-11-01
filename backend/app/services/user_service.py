"""User service."""

from typing import Optional

from sqlalchemy.orm import Session

from app.models.refresh_token import RefreshToken
from app.models.user import User


class UserService:
    """Service for user operations."""

    # Profile fields that can be updated
    ALLOWED_PROFILE_FIELDS = {
        "full_name",
        "age",
        "height",
        "weight",
        "target_weight",
        "language",
        "timezone",
        "water_goal",
        "calorie_goal",
        "sleep_goal",
    }

    @staticmethod
    def update_profile(db: Session, user_id: int, **kwargs) -> User:
        """Update user profile fields.

        Args:
            db: Database session
            user_id: User ID
            **kwargs: Profile fields to update

        Returns:
            Updated User object

        Raises:
            ValueError: If user not found or invalid fields provided
        """
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise ValueError(f"User with id {user_id} not found")

        # Filter and validate fields
        for field, value in kwargs.items():
            if field not in UserService.ALLOWED_PROFILE_FIELDS:
                raise ValueError(f"Field '{field}' is not allowed to be updated")

            # Additional validation
            if field == "age" and value is not None:
                if value < 10 or value > 120:
                    raise ValueError("Age must be between 10 and 120")

            if field == "height" and value is not None:
                if value < 50 or value > 300:
                    raise ValueError("Height must be between 50 and 300 cm")

            if field == "weight" and value is not None:
                if value < 20 or value > 500:
                    raise ValueError("Weight must be between 20 and 500 kg")

            if field == "target_weight" and value is not None:
                if value < 20 or value > 500:
                    raise ValueError("Target weight must be between 20 and 500 kg")

            if field == "water_goal" and value is not None:
                if value < 0 or value > 10:
                    raise ValueError("Water goal must be between 0 and 10 liters")

            if field == "calorie_goal" and value is not None:
                if value < 0 or value > 10000:
                    raise ValueError("Calorie goal must be between 0 and 10000")

            if field == "sleep_goal" and value is not None:
                if value < 0 or value > 24:
                    raise ValueError("Sleep goal must be between 0 and 24 hours")

            # Set the value
            setattr(user, field, value)

        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            User object or None if not found
        """
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email.

        Args:
            db: Database session
            email: User email

        Returns:
            User object or None if not found
        """
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def delete_account(db: Session, user_id: int) -> bool:
        """Delete user account and all related data.

        This performs a hard delete. All related data (days, goals, refresh tokens,
        notifications) will be automatically deleted due to CASCADE configuration
        in the model relationships.

        Args:
            db: Database session
            user_id: User ID to delete

        Returns:
            True if user was deleted, False if user not found
        """
        # Get the user
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            return False

        # First, revoke all refresh tokens for this user
        # (This will happen automatically via CASCADE, but doing it explicitly
        # for clarity and to ensure any cleanup logic runs)
        db.query(RefreshToken).filter(RefreshToken.user_id == user_id).delete()

        # Delete the user (CASCADE will handle related data)
        db.delete(user)
        db.commit()

        return True
