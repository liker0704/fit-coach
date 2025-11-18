"""Meal endpoints."""

import asyncio
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.agents.agents.vision_agent import VisionAgent
from app.config import settings
from app.core.dependencies import get_current_user, get_db
from app.core.file_validator import validate_image_upload
from app.models.day import Day
from app.models.meal import Meal
from app.models.user import User
from app.schemas.meal import (
    MealCreate,
    MealProcessingStatus,
    MealResponse,
    MealUpdate,
    PhotoUploadResponse,
)
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


# Vision Agent integration


def process_meal_photo_background(meal_id: int, photo_path: str, user_id: int) -> None:
    """Process meal photo with Vision Agent in background.

    Args:
        meal_id: ID of the meal to update
        photo_path: Path to the uploaded photo
        user_id: User ID for database session
    """
    import asyncio
    from app.core.database import SessionLocal

    db = SessionLocal()

    async def _async_process():
        """Inner async function to run VisionAgent."""
        nonlocal db
        try:
            # Get meal and update status to processing
            meal = db.query(Meal).filter(Meal.id == meal_id).first()
            if not meal:
                return

            meal.photo_processing_status = "processing"
            db.commit()

            # Initialize Vision Agent
            vision_agent = VisionAgent(db=db, user_id=user_id)

            # Process photo
            result = await vision_agent.execute({
                "photo_path": photo_path,
                "category": meal.category,
                "day_id": meal.day_id,
            })

            # Update meal with results
            if result.get("success"):
                meal.photo_processing_status = "completed"
                if result.get("recognized_items"):
                    meal.ai_recognized_items = result["recognized_items"]
            else:
                meal.photo_processing_status = "failed"
                meal.photo_processing_error = result.get("error", "Unknown error")

            db.commit()

        except Exception as e:
            # Update meal with error
            meal = db.query(Meal).filter(Meal.id == meal_id).first()
            if meal:
                meal.photo_processing_status = "failed"
                meal.photo_processing_error = str(e)
                db.commit()
        finally:
            db.close()

    # Run async function
    asyncio.run(_async_process())


@router.post("/meals/upload-photo", response_model=PhotoUploadResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_meal_photo(
    day_id: int,
    category: str,
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload a meal photo and process it with Vision Agent.

    This endpoint:
    1. Validates the uploaded file (format, size)
    2. Saves the file to disk
    3. Creates a new meal record with status='processing'
    4. Triggers Vision Agent in background to:
       - Recognize food items in the photo
       - Search for nutrition information
       - Update the meal with nutrition data

    Args:
        day_id: Day ID to associate meal with
        category: Meal category (breakfast/lunch/dinner/snack)
        file: Uploaded photo file
        background_tasks: FastAPI background tasks
        db: Database session
        current_user: Current authenticated user

    Returns:
        PhotoUploadResponse with meal_id and status='processing'

    Raises:
        HTTPException: 400 if invalid file, 404 if day not found, 403 if not authorized
    """
    # Validate day exists and belongs to user
    day = db.query(Day).filter(Day.id == day_id).first()
    if not day:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Day with id {day_id} not found",
        )

    if day.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to add meals to this day",
        )

    # Validate uploaded file (security checks)
    safe_filename = await validate_image_upload(file)

    # Create meal_photos directory if not exists
    upload_dir = Path(settings.MEAL_PHOTOS_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Generate unique filename using sanitized filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    file_ext = Path(safe_filename).suffix
    filename = f"{current_user.id}_{timestamp}_{unique_id}{file_ext}"
    file_path = upload_dir / filename

    # Save file
    try:
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}",
        )

    # Create meal record with status='processing'
    meal_data = {
        "category": category,
        "photo_path": str(file_path),
        "photo_processing_status": "processing",
    }

    try:
        meal = MealService.create_meal(db, day_id, meal_data)
    except ValueError as e:
        # Clean up uploaded file
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # Trigger Vision Agent in background
    background_tasks.add_task(
        process_meal_photo_background,
        meal_id=meal.id,
        photo_path=str(file_path),
        user_id=current_user.id,
    )

    return PhotoUploadResponse(
        meal_id=meal.id,
        status="processing",
        message="Photo uploaded successfully. Processing in background...",
        photo_path=str(file_path),
    )


@router.get("/meals/{meal_id}/processing-status", response_model=MealProcessingStatus)
def get_meal_processing_status(
    meal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get the processing status of a meal photo.

    Use this endpoint to poll for Vision Agent processing results.
    Poll every 2-3 seconds until status is 'completed' or 'failed'.

    Args:
        meal_id: Meal ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        MealProcessingStatus with current status and results (if completed)

    Raises:
        HTTPException: 404 if meal not found, 403 if not authorized
    """
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
            detail="Not authorized to view this meal",
        )

    response = MealProcessingStatus(
        meal_id=meal.id,
        status=meal.photo_processing_status or "pending",
        error=meal.photo_processing_error,
        recognized_items=meal.ai_recognized_items,
    )

    # If completed, include full meal data
    if meal.photo_processing_status == "completed":
        response.meal_data = MealResponse.model_validate(meal)

    return response
