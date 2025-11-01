"""AI coaching and summary endpoints."""

from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.day import Day
from app.models.user import User
from app.schemas.ai import (
    CoachingRequest,
    CoachingResponse,
    SummaryRequest,
    SummaryResponse,
)
from app.services.llm_service import LLMService

router = APIRouter()


@router.post("/coaching", response_model=CoachingResponse)
def get_coaching_advice(
    request: CoachingRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get personalized AI coaching advice.

    Args:
        request: Coaching request with context
        db: Database session
        current_user: Authenticated user

    Returns:
        CoachingResponse with AI-generated advice

    Raises:
        HTTPException: 500 if LLM service fails
    """
    # Prepare user data for LLM
    user_data = {
        "full_name": current_user.full_name or "User",
        "age": current_user.age,
        "weight": float(current_user.weight) if current_user.weight else None,
        "target_weight": (
            float(current_user.target_weight) if current_user.target_weight else None
        ),
        "height": float(current_user.height) if current_user.height else None,
        "water_goal": (
            float(current_user.water_goal) if current_user.water_goal else None
        ),
        "calorie_goal": current_user.calorie_goal,
        "sleep_goal": float(current_user.sleep_goal) if current_user.sleep_goal else None,
    }

    try:
        advice = LLMService.generate_coaching_advice(
            user_data=user_data, context=request.context
        )

        return CoachingResponse(advice=advice, generated_at=datetime.utcnow())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate coaching advice: {str(e)}",
        )


@router.post("/summary", response_model=SummaryResponse)
def get_health_summary(
    request: SummaryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate AI-powered health summary.

    Args:
        request: Summary request with period and optional date
        db: Database session
        current_user: Authenticated user

    Returns:
        SummaryResponse with AI-generated summary

    Raises:
        HTTPException: 400 if invalid period, 500 if LLM fails
    """
    # Validate period
    if request.period not in ["daily", "weekly", "monthly"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Period must be 'daily', 'weekly', or 'monthly'",
        )

    # Calculate date range
    end_date = request.date or date.today()

    if request.period == "daily":
        start_date = end_date
        date_range = f"{start_date}"
    elif request.period == "weekly":
        start_date = end_date - timedelta(days=6)
        date_range = f"{start_date} to {end_date}"
    else:  # monthly
        start_date = end_date - timedelta(days=29)
        date_range = f"{start_date} to {end_date}"

    # Fetch user's days in the date range
    days = (
        db.query(Day)
        .filter(
            Day.user_id == current_user.id,
            Day.date >= start_date,
            Day.date <= end_date,
        )
        .all()
    )

    # Aggregate health data
    total_meals = sum(len(day.meals) for day in days)
    total_exercises = sum(len(day.exercises) for day in days)
    total_water = sum(
        sum(float(w.amount) for w in day.water_intakes) for day in days
    )

    sleep_records = [s for day in days for s in day.sleep_records]
    avg_sleep = (
        sum(float(s.duration) for s in sleep_records if s.duration) / len(sleep_records)
        if sleep_records
        else None
    )

    mood_records = [m for day in days for m in day.mood_records]
    avg_mood = (
        sum(m.mood_level for m in mood_records) / len(mood_records)
        if mood_records
        else None
    )

    notes_count = sum(len(day.notes) for day in days)

    # Prepare data for LLM
    health_data = {
        "period": request.period,
        "days_count": len(days),
        "meals_count": total_meals,
        "exercises_count": total_exercises,
        "total_water_liters": round(total_water, 1),
        "avg_sleep_hours": round(avg_sleep, 1) if avg_sleep else None,
        "avg_mood": round(avg_mood, 1) if avg_mood else None,
        "notes_count": notes_count,
    }

    try:
        summary = LLMService.generate_summary(data=health_data, period=request.period)

        return SummaryResponse(
            summary=summary,
            period=request.period,
            date_range=date_range,
            generated_at=datetime.utcnow(),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate summary: {str(e)}",
        )
