"""Sleep service."""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.sleep_record import SleepRecord


class SleepService:
    """Service for sleep operations."""

    @staticmethod
    def create_sleep(db: Session, day_id: int, sleep_data: dict) -> SleepRecord:
        """Create new sleep record for a day.

        Args:
            db: Database session
            day_id: Day ID to associate sleep record with
            sleep_data: Dictionary containing sleep record fields

        Returns:
            Newly created SleepRecord object

        Raises:
            ValueError: If required fields are missing
        """
        new_sleep = SleepRecord(day_id=day_id, **sleep_data)
        db.add(new_sleep)
        db.commit()
        db.refresh(new_sleep)
        return new_sleep

    @staticmethod
    def get_sleep(db: Session, sleep_id: int) -> Optional[SleepRecord]:
        """Get sleep record by ID.

        Args:
            db: Database session
            sleep_id: Sleep record ID

        Returns:
            SleepRecord object or None if not found
        """
        return db.query(SleepRecord).filter(SleepRecord.id == sleep_id).first()

    @staticmethod
    def get_sleep_by_day(db: Session, day_id: int) -> List[SleepRecord]:
        """Get all sleep records for a specific day.

        Args:
            db: Database session
            day_id: Day ID

        Returns:
            List of SleepRecord objects ordered by bedtime (nulls last)
        """
        return (
            db.query(SleepRecord)
            .filter(SleepRecord.day_id == day_id)
            .order_by(SleepRecord.bedtime.asc().nullslast())
            .all()
        )

    @staticmethod
    def update_sleep(db: Session, sleep_id: int, **kwargs) -> SleepRecord:
        """Update sleep record with field validation.

        Args:
            db: Database session
            sleep_id: Sleep record ID
            **kwargs: Fields to update (bedtime, wake_time, duration, quality,
                     deep_sleep, rem_sleep, interruptions, notes)

        Returns:
            Updated SleepRecord object

        Raises:
            ValueError: If sleep record not found
        """
        sleep = db.query(SleepRecord).filter(SleepRecord.id == sleep_id).first()

        if not sleep:
            raise ValueError(f"Sleep record with id {sleep_id} not found")

        # Update allowed fields
        allowed_fields = {
            "bedtime",
            "wake_time",
            "duration",
            "quality",
            "deep_sleep",
            "rem_sleep",
            "interruptions",
            "notes",
        }
        for field, value in kwargs.items():
            if field in allowed_fields:
                setattr(sleep, field, value)

        db.commit()
        db.refresh(sleep)
        return sleep

    @staticmethod
    def delete_sleep(db: Session, sleep_id: int) -> bool:
        """Delete sleep record.

        Args:
            db: Database session
            sleep_id: Sleep record ID

        Returns:
            True if deleted, False if not found
        """
        sleep = db.query(SleepRecord).filter(SleepRecord.id == sleep_id).first()

        if not sleep:
            return False

        db.delete(sleep)
        db.commit()
        return True
