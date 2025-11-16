"""Meal plan API endpoints."""

import logging
from typing import AsyncIterator

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.meal_plan import MealPlan
from app.models.user import User
from app.schemas.meal_plan import (
    MealPlanCreateResponse,
    MealPlanGenerateRequest,
    MealPlanListResponse,
    MealPlanResponse,
)
from app.services.meal_plan_service import MealPlanService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/generate", response_model=MealPlanCreateResponse)
async def generate_meal_plan(
    request: MealPlanGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate a new 7-day meal plan.

    Args:
        request: Meal plan generation request
        db: Database session
        current_user: Current authenticated user

    Returns:
        MealPlanCreateResponse with generated plan

    Raises:
        HTTPException: 500 if generation fails
    """
    try:
        logger.info(f"Generating meal plan for user {current_user.id}")

        # Generate meal plan
        result = MealPlanService.generate_7day_meal_plan(
            db=db,
            user=current_user,
            dietary_preferences=request.dietary_preferences,
            calorie_target=request.calorie_target,
            allergies=request.allergies,
        )

        if not result["success"]:
            return MealPlanCreateResponse(
                success=False,
                meal_plan=None,
                error=result.get("error", "Failed to generate meal plan")
            )

        # Save to database
        meal_plan = MealPlan(
            user_id=current_user.id,
            name=request.name or "My Meal Plan",
            description=request.description,
            calorie_target=result.get("calorie_target", 2000),
            dietary_preferences=request.dietary_preferences,
            allergies=request.allergies,
            plan_data=result.get("meal_plan", {}),
            summary=result.get("summary", {}),
            is_active=1,
        )

        db.add(meal_plan)
        db.commit()
        db.refresh(meal_plan)

        logger.info(f"Meal plan created successfully: ID {meal_plan.id}")

        return MealPlanCreateResponse(
            success=True,
            meal_plan=MealPlanResponse.model_validate(meal_plan),
            error=None
        )

    except Exception as e:
        logger.error(f"Error generating meal plan: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate meal plan: {str(e)}"
        )


@router.get("/", response_model=MealPlanListResponse)
async def get_meal_plans(
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all meal plans for current user.

    Args:
        active_only: Only return active plans (default True)
        db: Database session
        current_user: Current authenticated user

    Returns:
        MealPlanListResponse with list of plans
    """
    try:
        query = db.query(MealPlan).filter(MealPlan.user_id == current_user.id)

        if active_only:
            query = query.filter(MealPlan.is_active == 1)

        meal_plans = query.order_by(MealPlan.created_at.desc()).all()

        return MealPlanListResponse(
            meal_plans=[MealPlanResponse.model_validate(plan) for plan in meal_plans],
            total=len(meal_plans)
        )

    except Exception as e:
        logger.error(f"Error fetching meal plans: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch meal plans: {str(e)}"
        )


@router.get("/{plan_id}", response_model=MealPlanResponse)
async def get_meal_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific meal plan by ID.

    Args:
        plan_id: Meal plan ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        MealPlanResponse

    Raises:
        HTTPException: 404 if plan not found
    """
    try:
        meal_plan = db.query(MealPlan).filter(
            MealPlan.id == plan_id,
            MealPlan.user_id == current_user.id
        ).first()

        if not meal_plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meal plan not found"
            )

        return MealPlanResponse.model_validate(meal_plan)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching meal plan: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch meal plan: {str(e)}"
        )


@router.delete("/{plan_id}")
async def delete_meal_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete (archive) a meal plan.

    Args:
        plan_id: Meal plan ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Success message

    Raises:
        HTTPException: 404 if plan not found
    """
    try:
        meal_plan = db.query(MealPlan).filter(
            MealPlan.id == plan_id,
            MealPlan.user_id == current_user.id
        ).first()

        if not meal_plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meal plan not found"
            )

        # Archive instead of delete
        meal_plan.is_active = 0
        db.commit()

        return {"success": True, "message": "Meal plan archived successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting meal plan: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete meal plan: {str(e)}"
        )


@router.post("/generate/stream")
async def stream_meal_plan_generation(
    request: MealPlanGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Stream meal plan generation in real-time.

    Args:
        request: Meal plan generation request
        db: Database session
        current_user: Current authenticated user

    Returns:
        StreamingResponse with SSE format
    """
    try:
        logger.info(f"Streaming meal plan generation for user {current_user.id}")

        async def generate_stream() -> AsyncIterator[bytes]:
            """Generate SSE stream."""
            try:
                async for chunk in MealPlanService.stream_meal_plan_generation(
                    db=db,
                    user=current_user,
                    dietary_preferences=request.dietary_preferences,
                    calorie_target=request.calorie_target,
                    allergies=request.allergies,
                ):
                    yield f"data: {chunk}\n\n".encode("utf-8")
            except Exception as e:
                logger.error(f"Error in meal plan stream: {e}", exc_info=True)
                yield f"data: [ERROR: {str(e)}]\n\n".encode("utf-8")
            finally:
                yield "data: [DONE]\n\n".encode("utf-8")

        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            }
        )

    except Exception as e:
        logger.error(f"Error starting meal plan stream: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stream meal plan: {str(e)}"
        )
