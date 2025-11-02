"""Water intake endpoints."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.day import Day
from app.models.user import User
from app.models.water_intake import WaterIntake
from app.schemas.water import WaterCreate, WaterResponse, WaterUpdate
from app.services.water_service import WaterService

router = APIRouter()


@router.post(
    "/days/{day_id}/water-intakes",
    response_model=WaterResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_water_intake(
    day_id: int,
    water_data: WaterCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new water intake entry for a specific day.

    Args:
        day_id: Day ID to add water intake to
        water_data: Water intake data (amount, time)
        db: Database session
        current_user: Current authenticated user

    Returns:
        Newly created water intake entry

    Raises:
        HTTPException: 404 if day not found, 403 if not authorized
    """
    # Check if day exists
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
            detail="Not authorized to add water intake to this day",
        )

    # Create water intake
    water_intake = WaterService.create_water_intake(
        db, day_id, water_data.model_dump()
    )
    return water_intake


@router.get("/days/{day_id}/water-intakes", response_model=List[WaterResponse])
def get_water_intakes_by_day(
    day_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all water intake entries for a specific day.

    Args:
        day_id: Day ID to get water intakes for
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of water intake entries ordered by time

    Raises:
        HTTPException: 404 if day not found, 403 if not authorized
    """
    # Check if day exists
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
            detail="Not authorized to access this day's water intakes",
        )

    # Get water intakes
    water_intakes = WaterService.get_water_intakes_by_day(db, day_id)
    return water_intakes


@router.get("/water-intakes/{water_id}", response_model=WaterResponse)
def get_water_intake(
    water_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get specific water intake entry by ID.

    Args:
        water_id: Water intake ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Water intake entry

    Raises:
        HTTPException: 404 if water intake not found, 403 if not authorized
    """
    # Get water intake
    water_intake = WaterService.get_water_intake(db, water_id)

    if not water_intake:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Water intake with id {water_id} not found",
        )

    # Verify water intake's day belongs to current user
    if water_intake.day.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this water intake",
        )

    return water_intake


@router.put("/water-intakes/{water_id}", response_model=WaterResponse)
def update_water_intake(
    water_id: int,
    water_data: WaterUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update water intake entry.

    Args:
        water_id: Water intake ID to update
        water_data: Water intake update data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Updated water intake entry

    Raises:
        HTTPException: 404 if water intake not found, 403 if not authorized
    """
    # First check if water intake exists
    water_intake = db.query(WaterIntake).filter(WaterIntake.id == water_id).first()

    if not water_intake:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Water intake with id {water_id} not found",
        )

    # Verify water intake's day belongs to current user
    if water_intake.day.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this water intake",
        )

    # Update water intake with only the fields that are provided
    update_data = water_data.model_dump(exclude_unset=True)

    try:
        updated_water_intake = WaterService.update_water_intake(
            db, water_id, **update_data
        )
        return updated_water_intake
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.delete("/water-intakes/{water_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_water_intake(
    water_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete water intake entry.

    Args:
        water_id: Water intake ID to delete
        db: Database session
        current_user: Current authenticated user

    Returns:
        No content (204)

    Raises:
        HTTPException: 404 if water intake not found, 403 if not authorized
    """
    # First check if water intake exists
    water_intake = db.query(WaterIntake).filter(WaterIntake.id == water_id).first()

    if not water_intake:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Water intake with id {water_id} not found",
        )

    # Verify water intake's day belongs to current user
    if water_intake.day.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this water intake",
        )

    # Delete water intake
    success = WaterService.delete_water_intake(db, water_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Water intake with id {water_id} not found",
        )

    return None
