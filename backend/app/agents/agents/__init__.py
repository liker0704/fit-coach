"""Individual agent implementations package.

This package contains specialized agent implementations for different
use cases in the FitCoach application.
"""

from app.agents.agents.chatbot import ChatbotAgent
from app.agents.agents.daily_summary import DailySummaryAgent
from app.agents.agents.nutrition_coach import NutritionCoachAgent
from app.agents.agents.vision_agent import VisionAgent
from app.agents.agents.workout_coach import WorkoutCoachAgent

__all__ = [
    "VisionAgent",
    "DailySummaryAgent",
    "ChatbotAgent",
    "NutritionCoachAgent",
    "WorkoutCoachAgent",
]
