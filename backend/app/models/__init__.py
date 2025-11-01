"""Models package."""

# Import all models here for Alembic autogenerate
from app.models.day import Day
from app.models.exercise import Exercise, ExerciseSet
from app.models.goal import Goal
from app.models.llm_summary import LLMSummary
from app.models.meal import Meal, MealItem
from app.models.mood_record import MoodRecord
from app.models.note import Note
from app.models.notification import Notification
from app.models.refresh_token import RefreshToken
from app.models.sleep_record import SleepRecord
from app.models.user import User
from app.models.water_intake import WaterIntake

__all__ = [
    "User",
    "Day",
    "Meal",
    "MealItem",
    "Exercise",
    "ExerciseSet",
    "WaterIntake",
    "SleepRecord",
    "MoodRecord",
    "Note",
    "LLMSummary",
    "Goal",
    "RefreshToken",
    "Notification",
]
