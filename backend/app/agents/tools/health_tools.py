"""Health metrics and tracking tools for agents.

This module provides tools for agents to interact with health data,
vital signs, and progress tracking functionality.
"""

import logging
from datetime import date, datetime
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.models.day import Day
from app.models.goal import Goal
from app.models.user import User

logger = logging.getLogger(__name__)


def get_day_data(db: Session, user_id: int, target_date: Optional[date] = None) -> Dict[str, Any]:
    """Get comprehensive day data for a user.

    Retrieves all data for a specific day including meals, exercises, water,
    sleep, mood, and notes.

    Args:
        db: Database session
        user_id: User ID
        target_date: Target date (defaults to today)

    Returns:
        Dictionary with day data:
        {
            "date": "2025-01-07",
            "calories": 2150,
            "protein": 145.5,
            "carbs": 220.3,
            "fat": 68.2,
            "water_ml": 2500,
            "exercise_calories": 450,
            "sleep_hours": 7.5,
            "mood": "good",
            "meals": [...],
            "exercises": [...],
            "notes": "...",
            "goals": {...}
        }
    """
    if target_date is None:
        target_date = date.today()

    # Get or create day
    day = db.query(Day).filter(
        Day.user_id == user_id,
        Day.date == target_date
    ).first()

    if not day:
        logger.info(f"No data found for user {user_id} on {target_date}")
        return {
            "date": str(target_date),
            "has_data": False,
            "message": "No data logged for this day"
        }

    # Calculate totals from meals
    total_calories = sum(float(meal.calories or 0) for meal in day.meals)
    total_protein = sum(float(meal.protein or 0) for meal in day.meals)
    total_carbs = sum(float(meal.carbs or 0) for meal in day.meals)
    total_fat = sum(float(meal.fat or 0) for meal in day.meals)

    # Calculate exercise calories
    exercise_calories = sum(float(ex.calories_burned or 0) for ex in day.exercises)

    # Get user goals
    goals = db.query(Goal).filter(Goal.user_id == user_id).first()

    goals_data = {}
    if goals:
        goals_data = {
            "daily_calories": float(goals.daily_calories or 0),
            "daily_protein": float(goals.daily_protein or 0),
            "daily_carbs": float(goals.daily_carbs or 0),
            "daily_fat": float(goals.daily_fat or 0),
            "daily_water": float(goals.daily_water_ml or 0),
        }

    # Format meals
    meals_data = []
    for meal in day.meals:
        meals_data.append({
            "id": meal.id,
            "category": meal.category,
            "time": str(meal.time) if meal.time else None,
            "calories": float(meal.calories or 0),
            "protein": float(meal.protein or 0),
            "carbs": float(meal.carbs or 0),
            "fat": float(meal.fat or 0),
            "notes": meal.notes,
        })

    # Format exercises
    exercises_data = []
    for exercise in day.exercises:
        exercises_data.append({
            "id": exercise.id,
            "name": exercise.name,
            "type": exercise.type,
            "duration_minutes": exercise.duration_minutes,
            "calories_burned": float(exercise.calories_burned or 0),
            "notes": exercise.notes,
        })

    return {
        "date": str(target_date),
        "has_data": True,
        "nutrition": {
            "calories": round(total_calories, 1),
            "protein": round(total_protein, 1),
            "carbs": round(total_carbs, 1),
            "fat": round(total_fat, 1),
        },
        "water_ml": day.water_ml or 0,
        "exercise": {
            "calories_burned": round(exercise_calories, 1),
            "count": len(exercises_data),
        },
        "sleep": {
            "hours": float(day.sleep.hours or 0) if day.sleep else 0,
            "quality": day.sleep.quality if day.sleep else None,
        },
        "mood": {
            "level": day.mood.level if day.mood else None,
            "notes": day.mood.notes if day.mood else None,
        },
        "notes": day.note.content if day.note else None,
        "meals": meals_data,
        "exercises": exercises_data,
        "goals": goals_data,
    }


def get_user_profile(db: Session, user_id: int) -> Dict[str, Any]:
    """Get user profile information.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        User profile data
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        return {}

    return {
        "name": user.name,
        "email": user.email,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }


def get_user_goals(db: Session, user_id: int) -> Dict[str, Any]:
    """Get user's health and fitness goals.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        Goals data
    """
    goals = db.query(Goal).filter(Goal.user_id == user_id).first()

    if not goals:
        return {
            "has_goals": False,
            "message": "No goals set"
        }

    return {
        "has_goals": True,
        "weight_goal_kg": float(goals.weight_goal_kg or 0),
        "daily_calories": float(goals.daily_calories or 0),
        "daily_protein": float(goals.daily_protein or 0),
        "daily_carbs": float(goals.daily_carbs or 0),
        "daily_fat": float(goals.daily_fat or 0),
        "daily_water_ml": float(goals.daily_water_ml or 0),
        "weekly_workout_goal": goals.weekly_workout_goal or 0,
        "goal_type": goals.goal_type,
    }


def calculate_progress(db: Session, user_id: int, target_date: Optional[date] = None) -> Dict[str, Any]:
    """Calculate progress towards daily goals.

    Args:
        db: Database session
        user_id: User ID
        target_date: Target date (defaults to today)

    Returns:
        Progress data with percentages
    """
    if target_date is None:
        target_date = date.today()

    day_data = get_day_data(db, user_id, target_date)
    goals = get_user_goals(db, user_id)

    if not day_data.get("has_data") or not goals.get("has_goals"):
        return {
            "has_progress": False,
            "message": "Insufficient data for progress calculation"
        }

    nutrition = day_data["nutrition"]

    def calc_percentage(actual: float, target: float) -> float:
        """Calculate percentage, handle division by zero."""
        if target == 0:
            return 0.0
        return round((actual / target) * 100, 1)

    return {
        "has_progress": True,
        "calories": {
            "actual": nutrition["calories"],
            "target": goals["daily_calories"],
            "percentage": calc_percentage(nutrition["calories"], goals["daily_calories"]),
        },
        "protein": {
            "actual": nutrition["protein"],
            "target": goals["daily_protein"],
            "percentage": calc_percentage(nutrition["protein"], goals["daily_protein"]),
        },
        "carbs": {
            "actual": nutrition["carbs"],
            "target": goals["daily_carbs"],
            "percentage": calc_percentage(nutrition["carbs"], goals["daily_carbs"]),
        },
        "fat": {
            "actual": nutrition["fat"],
            "target": goals["daily_fat"],
            "percentage": calc_percentage(nutrition["fat"], goals["daily_fat"]),
        },
        "water": {
            "actual": day_data["water_ml"],
            "target": goals["daily_water_ml"],
            "percentage": calc_percentage(day_data["water_ml"], goals["daily_water_ml"]),
        },
    }
