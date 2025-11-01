"""Mood endpoints."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.day import Day
from app.models.mood_record import MoodRecord
from app.models.user import User
from app.schemas.mood import MoodCreate, MoodResponse, MoodUpdate
from app.services.mood_service import MoodService

router = APIRouter()


@router.post("/days/{day_id}/moods", response_model=MoodResponse, status_code=status.HTTP_201_CREATED)
def create_mood(
    day_id: int,
    mood_data: MoodCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new mood record for a day.

    Args:
        day_id: Day ID to associate mood record with
        mood_data: Mood creation data
        db: Database session
        current_user: Current authenticated user

    Returns:
        MoodResponse with status 201

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
            detail="Not authorized to add mood records to this day",
        )

    # Create mood record (exclude day_id from mood_data as we use path parameter)
    mood_dict = mood_data.model_dump(exclude={"day_id"})

    try:
        mood = MoodService.create_mood(db, day_id, mood_dict)
        return mood
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/days/{day_id}/moods", response_model=List[MoodResponse])
def get_moods_by_day(
    day_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all mood records for a specific day.

    Args:
        day_id: Day ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of mood records ordered by time

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
            detail="Not authorized to view mood records for this day",
        )

    moods = MoodService.get_moods_by_day(db, day_id)
    return moods


@router.get("/moods/{mood_id}", response_model=MoodResponse)
def get_mood(
    mood_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get specific mood record by ID.

    Args:
        mood_id: Mood record ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Mood record data

    Raises:
        HTTPException: 404 if mood record not found, 403 if not authorized
    """
    mood = MoodService.get_mood(db, mood_id)

    if not mood:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mood record with id {mood_id} not found",
        )

    # Verify mood record's day belongs to current user
    if mood.day.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this mood record",
        )

    return mood


@router.put("/moods/{mood_id}", response_model=MoodResponse)
def update_mood(
    mood_id: int,
    mood_data: MoodUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update mood record information.

    Args:
        mood_id: Mood record ID to update
        mood_data: Mood update data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Updated mood record data

    Raises:
        HTTPException: 404 if mood record not found, 403 if not authorized
    """
    # First check if mood record exists
    mood = db.query(MoodRecord).filter(MoodRecord.id == mood_id).first()

    if not mood:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mood record with id {mood_id} not found",
        )

    # Verify mood record's day belongs to current user
    if mood.day.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this mood record",
        )

    # Update mood record with only the fields that are provided
    update_data = mood_data.model_dump(exclude_unset=True)

    try:
        updated_mood = MoodService.update_mood(db, mood_id, **update_data)
        return updated_mood
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.delete("/moods/{mood_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_mood(
    mood_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete mood record.

    Args:
        mood_id: Mood record ID to delete
        db: Database session
        current_user: Current authenticated user

    Returns:
        No content (204)

    Raises:
        HTTPException: 404 if mood record not found, 403 if not authorized
    """
    # First check if mood record exists
    mood = db.query(MoodRecord).filter(MoodRecord.id == mood_id).first()

    if not mood:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mood record with id {mood_id} not found",
        )

    # Verify mood record's day belongs to current user
    if mood.day.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this mood record",
        )

    # Delete mood record
    success = MoodService.delete_mood(db, mood_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mood record with id {mood_id} not found",
        )

    return None
