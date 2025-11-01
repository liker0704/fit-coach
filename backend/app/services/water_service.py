"""Water service."""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.water_intake import WaterIntake


class WaterService:
    """Service for water intake operations."""

    @staticmethod
    def create_water_intake(db: Session, day_id: int, water_data: dict) -> WaterIntake:
        """Create new water intake for a day.

        Args:
            db: Database session
            day_id: Day ID
            water_data: Dictionary containing water intake data (amount, time)

        Returns:
            Newly created WaterIntake object
        """
        water_intake = WaterIntake(day_id=day_id, **water_data)
        db.add(water_intake)
        db.commit()
        db.refresh(water_intake)
        return water_intake

    @staticmethod
    def get_water_intake(db: Session, water_id: int) -> Optional[WaterIntake]:
        """Get water intake by ID.

        Args:
            db: Database session
            water_id: Water intake ID

        Returns:
            WaterIntake object or None if not found
        """
        return db.query(WaterIntake).filter(WaterIntake.id == water_id).first()

    @staticmethod
    def get_water_intakes_by_day(db: Session, day_id: int) -> List[WaterIntake]:
        """Get all water intakes for a specific day.

        Args:
            db: Database session
            day_id: Day ID

        Returns:
            List of WaterIntake objects ordered by time
        """
        return (
            db.query(WaterIntake)
            .filter(WaterIntake.day_id == day_id)
            .order_by(WaterIntake.time)
            .all()
        )

    @staticmethod
    def update_water_intake(db: Session, water_id: int, **kwargs) -> WaterIntake:
        """Update water intake fields.

        Args:
            db: Database session
            water_id: Water intake ID
            **kwargs: Fields to update (amount, time)

        Returns:
            Updated WaterIntake object

        Raises:
            ValueError: If water intake not found
        """
        water_intake = db.query(WaterIntake).filter(WaterIntake.id == water_id).first()

        if not water_intake:
            raise ValueError(f"WaterIntake with id {water_id} not found")

        # Update allowed fields
        allowed_fields = {"amount", "time"}
        for field, value in kwargs.items():
            if field in allowed_fields:
                setattr(water_intake, field, value)

        db.commit()
        db.refresh(water_intake)
        return water_intake

    @staticmethod
    def delete_water_intake(db: Session, water_id: int) -> bool:
        """Delete water intake.

        Args:
            db: Database session
            water_id: Water intake ID

        Returns:
            True if deleted, False if not found
        """
        water_intake = db.query(WaterIntake).filter(WaterIntake.id == water_id).first()

        if not water_intake:
            return False

        db.delete(water_intake)
        db.commit()
        return True
