"""Exercise service."""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.exercise import Exercise


class ExerciseService:
    """Service for exercise operations."""

    @staticmethod
    def create_exercise(db: Session, day_id: int, exercise_data: dict) -> Exercise:
        """Create new exercise for a day.

        Args:
            db: Database session
            day_id: Day ID
            exercise_data: Dictionary containing exercise fields

        Returns:
            Newly created Exercise object

        Raises:
            ValueError: If required fields are missing
        """
        if "type" not in exercise_data:
            raise ValueError("Exercise type is required")

        new_exercise = Exercise(day_id=day_id, **exercise_data)
        db.add(new_exercise)
        db.commit()
        db.refresh(new_exercise)
        return new_exercise

    @staticmethod
    def get_exercise(db: Session, exercise_id: int) -> Optional[Exercise]:
        """Get exercise by ID.

        Args:
            db: Database session
            exercise_id: Exercise ID

        Returns:
            Exercise object or None if not found
        """
        return db.query(Exercise).filter(Exercise.id == exercise_id).first()

    @staticmethod
    def get_exercises_by_day(db: Session, day_id: int) -> List[Exercise]:
        """Get all exercises for a specific day.

        Args:
            db: Database session
            day_id: Day ID

        Returns:
            List of Exercise objects ordered by start_time
        """
        return (
            db.query(Exercise)
            .filter(Exercise.day_id == day_id)
            .order_by(Exercise.start_time)
            .all()
        )

    @staticmethod
    def update_exercise(db: Session, exercise_id: int, **kwargs) -> Exercise:
        """Update exercise fields.

        Args:
            db: Database session
            exercise_id: Exercise ID
            **kwargs: Fields to update (type, name, start_time, duration, distance,
                      calories_burned, heart_rate_avg, heart_rate_max, intensity, notes)

        Returns:
            Updated Exercise object

        Raises:
            ValueError: If exercise not found
        """
        exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()

        if not exercise:
            raise ValueError(f"Exercise with id {exercise_id} not found")

        # Update allowed fields
        allowed_fields = {
            "type",
            "name",
            "start_time",
            "duration",
            "distance",
            "calories_burned",
            "heart_rate_avg",
            "heart_rate_max",
            "intensity",
            "notes",
        }
        for field, value in kwargs.items():
            if field in allowed_fields:
                setattr(exercise, field, value)

        db.commit()
        db.refresh(exercise)
        return exercise

    @staticmethod
    def delete_exercise(db: Session, exercise_id: int) -> bool:
        """Delete exercise.

        Args:
            db: Database session
            exercise_id: Exercise ID

        Returns:
            True if deleted, False if not found
        """
        exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()

        if not exercise:
            return False

        db.delete(exercise)
        db.commit()
        return True
