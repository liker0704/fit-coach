"""Meal endpoints."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.day import Day
from app.models.meal import Meal
from app.models.user import User
from app.schemas.meal import MealCreate, MealResponse, MealUpdate
from app.services.meal_service import MealService

router = APIRouter()


@router.post("/days/{day_id}/meals", response_model=MealResponse, status_code=status.HTTP_201_CREATED)
def create_meal(
    day_id: int,
    meal_data: MealCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new meal for a day.

    Args:
        day_id: Day ID to associate meal with
        meal_data: Meal creation data
        db: Database session
        current_user: Current authenticated user

    Returns:
        MealResponse with status 201

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
            detail="Not authorized to add meals to this day",
        )

    # Create meal (exclude day_id from meal_data as we use path parameter)
    meal_dict = meal_data.model_dump(exclude={"day_id"})

    try:
        meal = MealService.create_meal(db, day_id, meal_dict)
        return meal
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/days/{day_id}/meals", response_model=List[MealResponse])
def get_meals_by_day(
    day_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all meals for a specific day.

    Args:
        day_id: Day ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of meals ordered by time

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
            detail="Not authorized to view meals for this day",
        )

    meals = MealService.get_meals_by_day(db, day_id)
    return meals


@router.get("/meals/{meal_id}", response_model=MealResponse)
def get_meal(
    meal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get specific meal by ID.

    Args:
        meal_id: Meal ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Meal data

    Raises:
        HTTPException: 404 if meal not found, 403 if not authorized
    """
    meal = MealService.get_meal(db, meal_id)

    if not meal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Meal with id {meal_id} not found",
        )

    # Verify meal's day belongs to current user
    if meal.day.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this meal",
        )

    return meal


@router.put("/meals/{meal_id}", response_model=MealResponse)
def update_meal(
    meal_id: int,
    meal_data: MealUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update meal information.

    Args:
        meal_id: Meal ID to update
        meal_data: Meal update data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Updated meal data

    Raises:
        HTTPException: 404 if meal not found, 403 if not authorized
    """
    # First check if meal exists
    meal = db.query(Meal).filter(Meal.id == meal_id).first()

    if not meal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Meal with id {meal_id} not found",
        )

    # Verify meal's day belongs to current user
    if meal.day.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this meal",
        )

    # Update meal with only the fields that are provided
    update_data = meal_data.model_dump(exclude_unset=True)

    try:
        updated_meal = MealService.update_meal(db, meal_id, **update_data)
        return updated_meal
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.delete("/meals/{meal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_meal(
    meal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete meal.

    Args:
        meal_id: Meal ID to delete
        db: Database session
        current_user: Current authenticated user

    Returns:
        No content (204)

    Raises:
        HTTPException: 404 if meal not found, 403 if not authorized
    """
    # First check if meal exists
    meal = db.query(Meal).filter(Meal.id == meal_id).first()

    if not meal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Meal with id {meal_id} not found",
        )

    # Verify meal's day belongs to current user
    if meal.day.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this meal",
        )

    # Delete meal
    success = MealService.delete_meal(db, meal_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Meal with id {meal_id} not found",
        )

    return None
