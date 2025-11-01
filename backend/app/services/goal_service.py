"""Goal service."""

from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.goal import Goal


class GoalService:
    """Service for goal operations."""

    @staticmethod
    def create_goal(db: Session, user_id: int, goal_data: dict) -> Goal:
        """Create new goal for a user.

        Args:
            db: Database session
            user_id: User ID to associate goal with
            goal_data: Dictionary containing goal fields

        Returns:
            Newly created Goal object

        Raises:
            ValueError: If required fields are missing
        """
        if "type" not in goal_data:
            raise ValueError("Goal type is required")
        if "title" not in goal_data:
            raise ValueError("Goal title is required")
        if "target_value" not in goal_data:
            raise ValueError("Goal target_value is required")
        if "start_date" not in goal_data:
            raise ValueError("Goal start_date is required")

        new_goal = Goal(user_id=user_id, **goal_data)
        db.add(new_goal)
        db.commit()
        db.refresh(new_goal)
        return new_goal

    @staticmethod
    def get_goal(db: Session, goal_id: int) -> Optional[Goal]:
        """Get goal by ID.

        Args:
            db: Database session
            goal_id: Goal ID

        Returns:
            Goal object or None if not found
        """
        return db.query(Goal).filter(Goal.id == goal_id).first()

    @staticmethod
    def get_user_goals(
        db: Session, user_id: int, status: Optional[str] = None
    ) -> List[Goal]:
        """Get all goals for a specific user.

        Args:
            db: Database session
            user_id: User ID
            status: Optional status filter (active, completed, archived)

        Returns:
            List of Goal objects ordered by created_at desc
        """
        query = db.query(Goal).filter(Goal.user_id == user_id)

        if status:
            query = query.filter(Goal.status == status)

        return query.order_by(Goal.created_at.desc()).all()

    @staticmethod
    def update_goal(db: Session, goal_id: int, **kwargs) -> Goal:
        """Update goal with field validation.

        Args:
            db: Database session
            goal_id: Goal ID
            **kwargs: Fields to update (type, title, description, target_value,
                     current_value, unit, start_date, end_date, status)

        Returns:
            Updated Goal object

        Raises:
            ValueError: If goal not found
        """
        goal = db.query(Goal).filter(Goal.id == goal_id).first()

        if not goal:
            raise ValueError(f"Goal with id {goal_id} not found")

        # Track if status is being changed to completed
        status_changed_to_completed = False
        if "status" in kwargs and kwargs["status"] == "completed":
            if goal.status != "completed":
                status_changed_to_completed = True

        # Update allowed fields
        allowed_fields = {
            "type",
            "title",
            "description",
            "target_value",
            "current_value",
            "unit",
            "start_date",
            "end_date",
            "status",
        }
        for field, value in kwargs.items():
            if field in allowed_fields:
                setattr(goal, field, value)

        # Auto-set completed_at when status changes to completed
        if status_changed_to_completed:
            goal.completed_at = datetime.utcnow()

        db.commit()
        db.refresh(goal)
        return goal

    @staticmethod
    def delete_goal(db: Session, goal_id: int) -> bool:
        """Delete goal.

        Args:
            db: Database session
            goal_id: Goal ID

        Returns:
            True if deleted, False if not found
        """
        goal = db.query(Goal).filter(Goal.id == goal_id).first()

        if not goal:
            return False

        db.delete(goal)
        db.commit()
        return True
