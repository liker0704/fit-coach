"""Exercise endpoints."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.day import Day
from app.models.exercise import Exercise
from app.models.user import User
from app.schemas.exercise import ExerciseCreate, ExerciseResponse, ExerciseUpdate
from app.services.exercise_service import ExerciseService

router = APIRouter()


@router.post(
    "/days/{day_id}/exercises",
    response_model=ExerciseResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_exercise(
    day_id: int,
    exercise_data: ExerciseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new exercise for a specific day.

    Args:
        day_id: Day ID to add exercise to
        exercise_data: Exercise creation data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Newly created exercise with 201 status

    Raises:
        HTTPException: 404 if day not found, 403 if not authorized
    """
    # First check if day exists
    day = db.query(Day).filter(Day.id == day_id).first()

    if not day:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Day with id {day_id} not found",
        )

    # Verify day belongs to current user
    if day.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to add exercises to this day",
        )

    # Create exercise
    exercise_dict = exercise_data.model_dump(exclude_unset=True)
    exercise = ExerciseService.create_exercise(db, day_id, exercise_dict)
    return exercise


@router.get("/days/{day_id}/exercises", response_model=List[ExerciseResponse])
def get_exercises_by_day(
    day_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all exercises for a specific day.

    Args:
        day_id: Day ID to get exercises for
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of exercises for the day, ordered by start_time

    Raises:
        HTTPException: 404 if day not found, 403 if not authorized
    """
    # First check if day exists
    day = db.query(Day).filter(Day.id == day_id).first()

    if not day:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Day with id {day_id} not found",
        )

    # Verify day belongs to current user
    if day.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view exercises for this day",
        )

    # Get exercises
    exercises = ExerciseService.get_exercises_by_day(db, day_id)
    return exercises


@router.get("/exercises/{exercise_id}", response_model=ExerciseResponse)
def get_exercise(
    exercise_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get specific exercise by ID.

    Args:
        exercise_id: Exercise ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Exercise data

    Raises:
        HTTPException: 404 if exercise not found, 403 if not authorized
    """
    exercise = ExerciseService.get_exercise(db, exercise_id)

    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exercise with id {exercise_id} not found",
        )

    # Verify exercise's day belongs to current user
    if exercise.day.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this exercise",
        )

    return exercise


@router.put("/exercises/{exercise_id}", response_model=ExerciseResponse)
def update_exercise(
    exercise_id: int,
    exercise_data: ExerciseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update exercise information.

    Args:
        exercise_id: Exercise ID to update
        exercise_data: Exercise update data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Updated exercise data

    Raises:
        HTTPException: 404 if exercise not found, 403 if not authorized
    """
    # First check if exercise exists
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()

    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exercise with id {exercise_id} not found",
        )

    # Verify exercise's day belongs to current user
    if exercise.day.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this exercise",
        )

    # Update exercise with only the fields that are provided
    update_data = exercise_data.model_dump(exclude_unset=True)

    try:
        updated_exercise = ExerciseService.update_exercise(db, exercise_id, **update_data)
        return updated_exercise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.delete("/exercises/{exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exercise(
    exercise_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete exercise.

    Args:
        exercise_id: Exercise ID to delete
        db: Database session
        current_user: Current authenticated user

    Returns:
        No content (204)

    Raises:
        HTTPException: 404 if exercise not found, 403 if not authorized
    """
    # First check if exercise exists
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()

    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exercise with id {exercise_id} not found",
        )

    # Verify exercise's day belongs to current user
    if exercise.day.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this exercise",
        )

    # Delete exercise
    success = ExerciseService.delete_exercise(db, exercise_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exercise with id {exercise_id} not found",
        )

    return None
