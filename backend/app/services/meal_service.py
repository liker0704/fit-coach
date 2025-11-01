"""Meal service."""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.meal import Meal


class MealService:
    """Service for meal operations."""

    @staticmethod
    def create_meal(db: Session, day_id: int, meal_data: dict) -> Meal:
        """Create new meal for a day.

        Args:
            db: Database session
            day_id: Day ID to associate meal with
            meal_data: Dictionary containing meal fields

        Returns:
            Newly created Meal object

        Raises:
            ValueError: If required fields are missing
        """
        if "category" not in meal_data:
            raise ValueError("Meal category is required")

        new_meal = Meal(day_id=day_id, **meal_data)
        db.add(new_meal)
        db.commit()
        db.refresh(new_meal)
        return new_meal

    @staticmethod
    def get_meal(db: Session, meal_id: int) -> Optional[Meal]:
        """Get meal by ID.

        Args:
            db: Database session
            meal_id: Meal ID

        Returns:
            Meal object or None if not found
        """
        return db.query(Meal).filter(Meal.id == meal_id).first()

    @staticmethod
    def get_meals_by_day(db: Session, day_id: int) -> List[Meal]:
        """Get all meals for a specific day.

        Args:
            db: Database session
            day_id: Day ID

        Returns:
            List of Meal objects ordered by time (nulls last)
        """
        return (
            db.query(Meal)
            .filter(Meal.day_id == day_id)
            .order_by(Meal.time.asc().nullslast())
            .all()
        )

    @staticmethod
    def update_meal(db: Session, meal_id: int, **kwargs) -> Meal:
        """Update meal with field validation.

        Args:
            db: Database session
            meal_id: Meal ID
            **kwargs: Fields to update (category, time, calories, protein, carbs,
                     fat, fiber, sugar, sodium, notes, photo_url)

        Returns:
            Updated Meal object

        Raises:
            ValueError: If meal not found
        """
        meal = db.query(Meal).filter(Meal.id == meal_id).first()

        if not meal:
            raise ValueError(f"Meal with id {meal_id} not found")

        # Update allowed fields
        allowed_fields = {
            "category",
            "time",
            "calories",
            "protein",
            "carbs",
            "fat",
            "fiber",
            "sugar",
            "sodium",
            "notes",
            "photo_url",
        }
        for field, value in kwargs.items():
            if field in allowed_fields:
                setattr(meal, field, value)

        db.commit()
        db.refresh(meal)
        return meal

    @staticmethod
    def delete_meal(db: Session, meal_id: int) -> bool:
        """Delete meal.

        Args:
            db: Database session
            meal_id: Meal ID

        Returns:
            True if deleted, False if not found
        """
        meal = db.query(Meal).filter(Meal.id == meal_id).first()

        if not meal:
            return False

        db.delete(meal)
        db.commit()
        return True
