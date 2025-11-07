"""Workout coach agent for exercise planning and fitness guidance."""

import logging
from datetime import date
from pathlib import Path
from typing import Any, Dict

from langchain.chat_models import init_chat_model
from sqlalchemy.orm import Session

from app.agents.base import BaseAgent
from app.agents.tools.health_tools import get_day_data, get_user_goals
from app.config import settings

logger = logging.getLogger(__name__)

# Load prompt
PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "workout_coach.txt"
try:
    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        SYSTEM_PROMPT = f.read().strip()
except Exception as e:
    logger.error(f"Failed to load workout coach prompt: {e}")
    SYSTEM_PROMPT = "You are a professional workout coach."


class WorkoutCoachAgent(BaseAgent):
    """Workout coach agent for fitness training and exercise programming.

    This agent provides workout plans, exercise suggestions, and fitness
    guidance based on user goals and fitness level.
    """

    def __init__(self, db_session: Session, user_id: int):
        """Initialize Workout Coach Agent.

        Args:
            db_session: SQLAlchemy database session
            user_id: ID of the user
        """
        super().__init__(db_session, user_id, "workout_coach")
        self.llm = init_chat_model(
            model=settings.LLM_MODEL_NAME,
            model_provider=settings.LLM_PROVIDER,
            temperature=settings.LLM_TEMPERATURE,
            max_tokens=settings.LLM_MAX_TOKENS,
        )
        logger.info(f"Workout Coach Agent initialized for user {user_id}")

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Provide workout coaching advice.

        Args:
            input_data: Dictionary with keys:
                - question (str): User's workout question
                - date (str, optional): Date to analyze (defaults to today)
                - conversation_history (list, optional): Previous messages

        Returns:
            Dictionary with response:
                - success (bool): Whether generation succeeded
                - response (str): Coach's response
                - context_data (dict): Workout data used
                - error (str, optional): Error message if failed
        """
        try:
            user_question = input_data.get("question")
            if not user_question:
                return {
                    "success": False,
                    "response": None,
                    "error": "No question provided"
                }

            logger.info(f"Processing workout coaching request for user {self.user_id}")

            # Parse target date
            target_date = input_data.get("date")
            if target_date:
                if isinstance(target_date, str):
                    target_date = date.fromisoformat(target_date)
            else:
                target_date = date.today()

            # Get user data
            day_data = get_day_data(self.db, self.user_id, target_date)
            goals = get_user_goals(self.db, self.user_id)

            # Format context
            context = self._format_workout_context(day_data, goals)

            # Build messages
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]

            # Add conversation history if provided
            conversation_history = input_data.get("conversation_history", [])
            if conversation_history:
                messages.extend(conversation_history)

            # Add context and question
            user_message = f"USER'S WORKOUT DATA:\n{context}\n\nQUESTION: {user_question}"
            messages.append({"role": "user", "content": user_message})

            # Generate response
            response = await self.llm.ainvoke(messages)
            response_text = response.content.strip()

            logger.info(f"Successfully generated workout coaching response")

            return {
                "success": True,
                "response": response_text,
                "context_data": {
                    "day_data": day_data,
                    "goals": goals
                },
                "error": None
            }

        except Exception as e:
            logger.error(f"Error generating workout coaching response: {e}", exc_info=True)
            return {
                "success": False,
                "response": None,
                "error": str(e)
            }

    def _format_workout_context(self, day_data: Dict[str, Any], goals: Dict[str, Any]) -> str:
        """Format workout data into context string for LLM."""
        lines = [
            f"Date: {day_data.get('date', 'today')}",
            "",
            "=== TODAY'S WORKOUTS ===",
        ]

        if day_data.get("has_data") and day_data.get("exercises"):
            for exercise in day_data["exercises"]:
                ex_line = f"- {exercise['name']} ({exercise['type']})"
                if exercise.get('duration_minutes'):
                    ex_line += f" - {exercise['duration_minutes']} min"
                if exercise.get('calories_burned'):
                    ex_line += f" - {exercise['calories_burned']} kcal burned"
                lines.append(ex_line)
                if exercise.get('notes'):
                    lines.append(f"  Notes: {exercise['notes']}")

            lines.extend([
                "",
                f"Total Exercise Sessions: {day_data['exercise']['count']}",
                f"Total Calories Burned: {day_data['exercise']['calories_burned']} kcal",
            ])
        else:
            lines.append("No workouts logged yet today")

        if goals.get("has_goals"):
            lines.extend([
                "",
                "=== FITNESS GOALS ===",
                f"Weekly Workout Goal: {goals['weekly_workout_goal']} sessions",
                f"Goal Type: {goals.get('goal_type', 'not set')}",
            ])

        # Add wellness data for context
        if day_data.get("has_data"):
            lines.extend([
                "",
                "=== WELLNESS ===",
            ])
            if day_data['sleep']['hours'] > 0:
                lines.append(f"Sleep: {day_data['sleep']['hours']} hours")
            if day_data['mood'].get('level'):
                lines.append(f"Mood: {day_data['mood']['level']}")

        return "\n".join(lines)
