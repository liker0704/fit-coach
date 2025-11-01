"""Day service."""

from datetime import date
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.day import Day


class DayService:
    """Service for day operations."""

    @staticmethod
    def get_or_create_day(db: Session, user_id: int, day_date: date) -> Day:
        """Get existing day or create a new one.

        Args:
            db: Database session
            user_id: User ID
            day_date: Date for the day

        Returns:
            Day object (existing or newly created)
        """
        # Try to get existing day
        day = (
            db.query(Day)
            .filter(Day.user_id == user_id, Day.date == day_date)
            .first()
        )

        if day:
            return day

        # Create new day
        new_day = Day(user_id=user_id, date=day_date)
        db.add(new_day)
        db.commit()
        db.refresh(new_day)
        return new_day

    @staticmethod
    def get_day(db: Session, user_id: int, day_date: date) -> Optional[Day]:
        """Get specific day for user.

        Args:
            db: Database session
            user_id: User ID
            day_date: Date for the day

        Returns:
            Day object or None if not found
        """
        return (
            db.query(Day)
            .filter(Day.user_id == user_id, Day.date == day_date)
            .first()
        )

    @staticmethod
    def get_days_range(
        db: Session, user_id: int, start_date: date, end_date: date
    ) -> List[Day]:
        """Get all days in date range for user.

        Args:
            db: Database session
            user_id: User ID
            start_date: Start date (inclusive)
            end_date: End date (inclusive)

        Returns:
            List of Day objects ordered by date
        """
        return (
            db.query(Day)
            .filter(
                Day.user_id == user_id,
                Day.date >= start_date,
                Day.date <= end_date,
            )
            .order_by(Day.date)
            .all()
        )

    @staticmethod
    def update_day(db: Session, day_id: int, **kwargs) -> Day:
        """Update day fields.

        Args:
            db: Database session
            day_id: Day ID
            **kwargs: Fields to update (tag, feeling, effort_score, summary, llm_advice)

        Returns:
            Updated Day object

        Raises:
            ValueError: If day not found
        """
        day = db.query(Day).filter(Day.id == day_id).first()

        if not day:
            raise ValueError(f"Day with id {day_id} not found")

        # Update allowed fields
        allowed_fields = {"tag", "feeling", "effort_score", "summary", "llm_advice"}
        for field, value in kwargs.items():
            if field in allowed_fields:
                setattr(day, field, value)

        db.commit()
        db.refresh(day)
        return day

    @staticmethod
    def delete_day(db: Session, day_id: int) -> bool:
        """Delete day.

        Args:
            db: Database session
            day_id: Day ID

        Returns:
            True if deleted, False if not found
        """
        day = db.query(Day).filter(Day.id == day_id).first()

        if not day:
            return False

        db.delete(day)
        db.commit()
        return True
