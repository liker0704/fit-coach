"""Mood service."""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.mood_record import MoodRecord


class MoodService:
    """Service for mood operations."""

    @staticmethod
    def create_mood(db: Session, day_id: int, mood_data: dict) -> MoodRecord:
        """Create new mood record for a day.

        Args:
            db: Database session
            day_id: Day ID to associate mood record with
            mood_data: Dictionary containing mood fields

        Returns:
            Newly created MoodRecord object

        Raises:
            ValueError: If required fields are missing
        """
        if "rating" not in mood_data:
            raise ValueError("Mood rating is required")

        new_mood = MoodRecord(day_id=day_id, **mood_data)
        db.add(new_mood)
        db.commit()
        db.refresh(new_mood)
        return new_mood

    @staticmethod
    def get_mood(db: Session, mood_id: int) -> Optional[MoodRecord]:
        """Get mood record by ID.

        Args:
            db: Database session
            mood_id: Mood record ID

        Returns:
            MoodRecord object or None if not found
        """
        return db.query(MoodRecord).filter(MoodRecord.id == mood_id).first()

    @staticmethod
    def get_moods_by_day(db: Session, day_id: int) -> List[MoodRecord]:
        """Get all mood records for a specific day.

        Args:
            db: Database session
            day_id: Day ID

        Returns:
            List of MoodRecord objects ordered by time
        """
        return (
            db.query(MoodRecord)
            .filter(MoodRecord.day_id == day_id)
            .order_by(MoodRecord.time.asc())
            .all()
        )

    @staticmethod
    def update_mood(db: Session, mood_id: int, **kwargs) -> MoodRecord:
        """Update mood record with field validation.

        Args:
            db: Database session
            mood_id: Mood record ID
            **kwargs: Fields to update (time, rating, energy_level, stress_level,
                     anxiety_level, tags, notes, ai_sentiment, ai_suggestions)

        Returns:
            Updated MoodRecord object

        Raises:
            ValueError: If mood record not found
        """
        mood = db.query(MoodRecord).filter(MoodRecord.id == mood_id).first()

        if not mood:
            raise ValueError(f"Mood record with id {mood_id} not found")

        # Update allowed fields
        allowed_fields = {
            "time",
            "rating",
            "energy_level",
            "stress_level",
            "anxiety_level",
            "tags",
            "notes",
            "ai_sentiment",
            "ai_suggestions",
        }
        for field, value in kwargs.items():
            if field in allowed_fields:
                setattr(mood, field, value)

        db.commit()
        db.refresh(mood)
        return mood

    @staticmethod
    def delete_mood(db: Session, mood_id: int) -> bool:
        """Delete mood record.

        Args:
            db: Database session
            mood_id: Mood record ID

        Returns:
            True if deleted, False if not found
        """
        mood = db.query(MoodRecord).filter(MoodRecord.id == mood_id).first()

        if not mood:
            return False

        db.delete(mood)
        db.commit()
        return True
