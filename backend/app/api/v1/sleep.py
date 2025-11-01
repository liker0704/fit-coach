"""Sleep endpoints."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.day import Day
from app.models.sleep_record import SleepRecord
from app.models.user import User
from app.schemas.sleep import SleepCreate, SleepResponse, SleepUpdate
from app.services.sleep_service import SleepService

router = APIRouter()


@router.post("/days/{day_id}/sleep", response_model=SleepResponse, status_code=status.HTTP_201_CREATED)
def create_sleep(
    day_id: int,
    sleep_data: SleepCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new sleep record for a day.

    Args:
        day_id: Day ID to associate sleep record with
        sleep_data: Sleep record creation data
        db: Database session
        current_user: Current authenticated user

    Returns:
        SleepResponse with status 201

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
            detail="Not authorized to add sleep records to this day",
        )

    # Create sleep record (exclude day_id from sleep_data as we use path parameter)
    sleep_dict = sleep_data.model_dump(exclude={"day_id"})

    try:
        sleep = SleepService.create_sleep(db, day_id, sleep_dict)
        return sleep
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/days/{day_id}/sleep", response_model=List[SleepResponse])
def get_sleep_by_day(
    day_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all sleep records for a specific day.

    Args:
        day_id: Day ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of sleep records ordered by bedtime

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
            detail="Not authorized to view sleep records for this day",
        )

    sleep_records = SleepService.get_sleep_by_day(db, day_id)
    return sleep_records


@router.get("/sleep/{sleep_id}", response_model=SleepResponse)
def get_sleep(
    sleep_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get specific sleep record by ID.

    Args:
        sleep_id: Sleep record ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Sleep record data

    Raises:
        HTTPException: 404 if sleep record not found, 403 if not authorized
    """
    sleep = SleepService.get_sleep(db, sleep_id)

    if not sleep:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sleep record with id {sleep_id} not found",
        )

    # Verify sleep record's day belongs to current user
    if sleep.day.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this sleep record",
        )

    return sleep


@router.put("/sleep/{sleep_id}", response_model=SleepResponse)
def update_sleep(
    sleep_id: int,
    sleep_data: SleepUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update sleep record information.

    Args:
        sleep_id: Sleep record ID to update
        sleep_data: Sleep record update data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Updated sleep record data

    Raises:
        HTTPException: 404 if sleep record not found, 403 if not authorized
    """
    # First check if sleep record exists
    sleep = db.query(SleepRecord).filter(SleepRecord.id == sleep_id).first()

    if not sleep:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sleep record with id {sleep_id} not found",
        )

    # Verify sleep record's day belongs to current user
    if sleep.day.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this sleep record",
        )

    # Update sleep record with only the fields that are provided
    update_data = sleep_data.model_dump(exclude_unset=True)

    try:
        updated_sleep = SleepService.update_sleep(db, sleep_id, **update_data)
        return updated_sleep
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.delete("/sleep/{sleep_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sleep(
    sleep_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete sleep record.

    Args:
        sleep_id: Sleep record ID to delete
        db: Database session
        current_user: Current authenticated user

    Returns:
        No content (204)

    Raises:
        HTTPException: 404 if sleep record not found, 403 if not authorized
    """
    # First check if sleep record exists
    sleep = db.query(SleepRecord).filter(SleepRecord.id == sleep_id).first()

    if not sleep:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sleep record with id {sleep_id} not found",
        )

    # Verify sleep record's day belongs to current user
    if sleep.day.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this sleep record",
        )

    # Delete sleep record
    success = SleepService.delete_sleep(db, sleep_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sleep record with id {sleep_id} not found",
        )

    return None
