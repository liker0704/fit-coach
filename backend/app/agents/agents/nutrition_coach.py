"""Nutrition coach agent for meal planning and dietary guidance."""

import logging
from datetime import date
from pathlib import Path
from typing import Any, Dict

from langchain.chat_models import init_chat_model
from sqlalchemy.orm import Session

from app.agents.base import BaseAgent
from app.agents.tools.health_tools import calculate_progress, get_day_data, get_user_goals
from app.config import settings

logger = logging.getLogger(__name__)

# Load prompt
PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "nutrition_coach.txt"
try:
    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        SYSTEM_PROMPT = f.read().strip()
except Exception as e:
    logger.error(f"Failed to load nutrition coach prompt: {e}")
    SYSTEM_PROMPT = "You are a professional nutrition coach."


class NutritionCoachAgent(BaseAgent):
    """Nutrition coach agent for dietary guidance and meal planning.

    This agent analyzes users' nutrition data, provides meal suggestions,
    and offers personalized dietary advice based on goals.
    """

    def __init__(self, db_session: Session, user_id: int):
        """Initialize Nutrition Coach Agent.

        Args:
            db_session: SQLAlchemy database session
            user_id: ID of the user
        """
        super().__init__(db_session, user_id, "nutrition_coach")
        self.llm = init_chat_model(
            model=settings.LLM_MODEL_NAME,
            model_provider=settings.LLM_PROVIDER,
            temperature=settings.LLM_TEMPERATURE,
            max_tokens=settings.LLM_MAX_TOKENS,
        )
        logger.info(f"Nutrition Coach Agent initialized for user {user_id}")

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Provide nutrition coaching advice.

        Args:
            input_data: Dictionary with keys:
                - question (str): User's nutrition question
                - date (str, optional): Date to analyze (defaults to today)
                - conversation_history (list, optional): Previous messages

        Returns:
            Dictionary with response:
                - success (bool): Whether generation succeeded
                - response (str): Coach's response
                - context_data (dict): Nutrition data used
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

            logger.info(f"Processing nutrition coaching request for user {self.user_id}")

            # Parse target date
            target_date = input_data.get("date")
            if target_date:
                if isinstance(target_date, str):
                    target_date = date.fromisoformat(target_date)
            else:
                target_date = date.today()

            # Get user data
            day_data = get_day_data(self.db, self.user_id, target_date)
            progress = calculate_progress(self.db, self.user_id, target_date)
            goals = get_user_goals(self.db, self.user_id)

            # Format context
            context = self._format_nutrition_context(day_data, progress, goals)

            # Build messages
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]

            # Add conversation history if provided
            conversation_history = input_data.get("conversation_history", [])
            if conversation_history:
                messages.extend(conversation_history)

            # Add context and question
            user_message = f"USER'S NUTRITION DATA:\n{context}\n\nQUESTION: {user_question}"
            messages.append({"role": "user", "content": user_message})

            # Generate response
            response = await self.llm.ainvoke(messages)
            response_text = response.content.strip()

            logger.info(f"Successfully generated nutrition coaching response")

            return {
                "success": True,
                "response": response_text,
                "context_data": {
                    "day_data": day_data,
                    "progress": progress,
                    "goals": goals
                },
                "error": None
            }

        except Exception as e:
            logger.error(f"Error generating nutrition coaching response: {e}", exc_info=True)
            return {
                "success": False,
                "response": None,
                "error": str(e)
            }

    def _format_nutrition_context(self, day_data: Dict[str, Any], progress: Dict[str, Any], goals: Dict[str, Any]) -> str:
        """Format nutrition data into context string for LLM."""
        lines = [
            f"Date: {day_data.get('date', 'today')}",
            "",
            "=== TODAY'S NUTRITION ===",
        ]

        if day_data.get("has_data"):
            nutrition = day_data["nutrition"]
            lines.extend([
                f"Calories: {nutrition['calories']} kcal",
                f"Protein: {nutrition['protein']}g",
                f"Carbs: {nutrition['carbs']}g",
                f"Fat: {nutrition['fat']}g",
                f"Water: {day_data['water_ml']}ml",
            ])

            if day_data.get("meals"):
                lines.extend(["", "=== MEALS ==="])
                for meal in day_data["meals"]:
                    lines.append(f"{meal['category'].title()}: {meal['calories']} kcal (P:{meal['protein']}g C:{meal['carbs']}g F:{meal['fat']}g)")
        else:
            lines.append("No data logged yet today")

        if goals.get("has_goals"):
            lines.extend([
                "",
                "=== GOALS ===",
                f"Daily Calories: {goals['daily_calories']} kcal",
                f"Protein: {goals['daily_protein']}g",
                f"Carbs: {goals['daily_carbs']}g",
                f"Fat: {goals['daily_fat']}g",
                f"Water: {goals['daily_water_ml']}ml",
                f"Goal Type: {goals.get('goal_type', 'not set')}",
            ])

        if progress.get("has_progress"):
            lines.extend([
                "",
                "=== PROGRESS ===",
                f"Calories: {progress['calories']['percentage']}%",
                f"Protein: {progress['protein']['percentage']}%",
                f"Carbs: {progress['carbs']['percentage']}%",
                f"Fat: {progress['fat']['percentage']}%",
                f"Water: {progress['water']['percentage']}%",
            ])

        return "\n".join(lines)
