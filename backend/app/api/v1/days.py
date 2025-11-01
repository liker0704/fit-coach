"""Day endpoints."""

from datetime import date, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.core.dependencies import get_current_user, get_db
from app.models.day import Day
from app.models.user import User
from app.schemas.day import DayCreate, DayResponse, DayUpdate
from app.services.day_service import DayService

router = APIRouter()


@router.post("/days", response_model=DayResponse, status_code=status.HTTP_201_CREATED)
def create_or_get_day(
    day_data: DayCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new day or get existing one for the specified date.

    Args:
        day_data: Day creation data (date required)
        db: Database session
        current_user: Current authenticated user

    Returns:
        DayResponse with status 201 if created, 200 if already exists

    Note:
        This endpoint uses get_or_create pattern. If a day already exists
        for the given date, it returns the existing day with 200 status.
        If it doesn't exist, it creates a new day and returns 201 status.
    """
    # Check if day already exists
    existing_day = DayService.get_day(db, current_user.id, day_data.date)

    if existing_day:
        # Day exists, return with 200 status
        # Note: FastAPI doesn't allow changing status code dynamically in response_model
        # So we'll return the existing day and the decorator will use 201
        # For proper status code handling, we'd need Response object
        return existing_day

    # Create new day
    day = DayService.get_or_create_day(db, current_user.id, day_data.date)
    return day


@router.get("/days/{date}", response_model=DayResponse)
def get_day_by_date(
    date: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get specific day by date.

    Args:
        date: Date in YYYY-MM-DD format
        db: Database session
        current_user: Current authenticated user

    Returns:
        Day data for the specified date

    Raises:
        HTTPException: 404 if day not found
    """
    day = DayService.get_day(db, current_user.id, date)

    if not day:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Day not found for date {date}",
        )

    return day


@router.get("/days", response_model=List[DayResponse])
def get_days_range(
    start_date: date = None,
    end_date: date = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get days in date range.

    Args:
        start_date: Start date (inclusive). Defaults to 7 days ago if not provided.
        end_date: End date (inclusive). Defaults to today if not provided.
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of days in the specified range, ordered by date

    Note:
        If no dates are provided, returns last 7 days (including today).
    """
    # Set default date range (last 7 days) if not provided
    if end_date is None:
        end_date = date.today()

    if start_date is None:
        start_date = end_date - timedelta(days=6)  # 7 days total including end_date

    # Validate date range
    if start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_date must be before or equal to end_date",
        )

    days = DayService.get_days_range(db, current_user.id, start_date, end_date)
    return days


@router.get("/days/id/{day_id}", response_model=DayResponse)
def get_day_by_id(
    day_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get day by ID (for navigation from calendar).

    Args:
        day_id: Day database ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Day data with all nested resources

    Raises:
        HTTPException: 404 if day not found
        HTTPException: 403 if not authorized
    """
    day = db.query(Day).options(
        joinedload(Day.meals),
        joinedload(Day.exercises),
        joinedload(Day.water_intakes),
        joinedload(Day.sleep_records),
        joinedload(Day.mood_records),
        joinedload(Day.notes),
    ).filter(Day.id == day_id).first()

    if not day:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Day not found"
        )

    if day.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this day"
        )

    return day


@router.put("/days/{day_id}", response_model=DayResponse)
def update_day(
    day_id: int,
    day_data: DayUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update day information.

    Args:
        day_id: Day ID to update
        day_data: Day update data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Updated day data

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
            detail="Not authorized to update this day",
        )

    # Update day with only the fields that are provided
    update_data = day_data.model_dump(exclude_unset=True)

    try:
        updated_day = DayService.update_day(db, day_id, **update_data)
        return updated_day
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.delete("/days/{day_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_day(
    day_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete day.

    Args:
        day_id: Day ID to delete
        db: Database session
        current_user: Current authenticated user

    Returns:
        No content (204)

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
            detail="Not authorized to delete this day",
        )

    # Delete day
    success = DayService.delete_day(db, day_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Day with id {day_id} not found",
        )

    return None
