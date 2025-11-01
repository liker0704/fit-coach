"""Goal endpoints."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.goal import Goal
from app.models.user import User
from app.schemas.goal import GoalCreate, GoalResponse, GoalUpdate
from app.services.goal_service import GoalService

router = APIRouter()


@router.post("/goals", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
def create_goal(
    goal_data: GoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new goal for the current user.

    Args:
        goal_data: Goal creation data
        db: Database session
        current_user: Current authenticated user

    Returns:
        GoalResponse with status 201

    Raises:
        HTTPException: 400 if validation fails
    """
    goal_dict = goal_data.model_dump()

    try:
        goal = GoalService.create_goal(db, current_user.id, goal_dict)
        return goal
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/goals", response_model=List[GoalResponse])
def get_goals(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status: active, completed, archived"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all goals for the current user.

    Args:
        status_filter: Optional status filter (active, completed, archived)
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of goals ordered by created_at desc

    Raises:
        HTTPException: 400 if invalid status provided
    """
    # Validate status if provided
    if status_filter and status_filter not in ["active", "completed", "archived"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status. Must be one of: active, completed, archived",
        )

    goals = GoalService.get_user_goals(db, current_user.id, status_filter)
    return goals


@router.get("/goals/{goal_id}", response_model=GoalResponse)
def get_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get specific goal by ID.

    Args:
        goal_id: Goal ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Goal data

    Raises:
        HTTPException: 404 if goal not found, 403 if not authorized
    """
    goal = GoalService.get_goal(db, goal_id)

    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Goal with id {goal_id} not found",
        )

    # Verify goal belongs to current user
    if goal.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this goal",
        )

    return goal


@router.put("/goals/{goal_id}", response_model=GoalResponse)
def update_goal(
    goal_id: int,
    goal_data: GoalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update goal information.

    Args:
        goal_id: Goal ID to update
        goal_data: Goal update data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Updated goal data

    Raises:
        HTTPException: 404 if goal not found, 403 if not authorized
    """
    # First check if goal exists
    goal = db.query(Goal).filter(Goal.id == goal_id).first()

    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Goal with id {goal_id} not found",
        )

    # Verify goal belongs to current user
    if goal.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this goal",
        )

    # Update goal with only the fields that are provided
    update_data = goal_data.model_dump(exclude_unset=True)

    try:
        updated_goal = GoalService.update_goal(db, goal_id, **update_data)
        return updated_goal
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.delete("/goals/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete goal.

    Args:
        goal_id: Goal ID to delete
        db: Database session
        current_user: Current authenticated user

    Returns:
        No content (204)

    Raises:
        HTTPException: 404 if goal not found, 403 if not authorized
    """
    # First check if goal exists
    goal = db.query(Goal).filter(Goal.id == goal_id).first()

    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Goal with id {goal_id} not found",
        )

    # Verify goal belongs to current user
    if goal.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this goal",
        )

    # Delete goal
    success = GoalService.delete_goal(db, goal_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Goal with id {goal_id} not found",
        )

    return None
