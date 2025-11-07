"""Daily summary agent for generating personalized daily reports."""

import json
import logging
from datetime import date
from pathlib import Path
from typing import Any, Dict, Optional

from langchain.chat_models import init_chat_model
from sqlalchemy.orm import Session

from app.agents.base import BaseAgent
from app.agents.tools.health_tools import calculate_progress, get_day_data
from app.config import settings

logger = logging.getLogger(__name__)

# Load prompt
PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "daily_summary.txt"
try:
    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        SYSTEM_PROMPT = f.read().strip()
except Exception as e:
    logger.error(f"Failed to load daily summary prompt: {e}")
    SYSTEM_PROMPT = "You are a helpful daily summary assistant."


class DailySummaryAgent(BaseAgent):
    """Agent for generating personalized daily summary reports.

    This agent analyzes user's daily activity (meals, exercises, sleep, etc.)
    and generates a comprehensive summary with insights and recommendations.
    """

    def __init__(self, db_session: Session, user_id: int):
        """Initialize Daily Summary Agent.

        Args:
            db_session: SQLAlchemy database session
            user_id: ID of the user
        """
        super().__init__(db_session, user_id, "daily_summary")
        self.llm = init_chat_model(
            model=settings.LLM_MODEL_NAME,
            model_provider=settings.LLM_PROVIDER,
            temperature=settings.LLM_TEMPERATURE,
            max_tokens=settings.LLM_MAX_TOKENS,
        )
        logger.info(f"Daily Summary Agent initialized for user {user_id}")

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate daily summary for a specific date.

        Args:
            input_data: Dictionary with optional keys:
                - date (str): Target date (defaults to today)

        Returns:
            Dictionary with summary:
                - success (bool): Whether generation succeeded
                - summary (str): Generated summary text
                - data (dict): Day data used for summary
                - error (str, optional): Error message if failed
        """
        try:
            # Parse target date
            target_date = input_data.get("date")
            if target_date:
                if isinstance(target_date, str):
                    target_date = date.fromisoformat(target_date)
            else:
                target_date = date.today()

            logger.info(f"Generating daily summary for {target_date}")

            # Get day data
            day_data = get_day_data(self.db, self.user_id, target_date)

            if not day_data.get("has_data"):
                return {
                    "success": False,
                    "summary": None,
                    "data": day_data,
                    "error": "No data logged for this day"
                }

            # Get progress
            progress = calculate_progress(self.db, self.user_id, target_date)

            # Format data for LLM
            user_data = self._format_data_for_llm(day_data, progress)

            # Generate summary using LLM
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Please analyze this day's data and generate a summary:\n\n{user_data}"}
            ]

            response = await self.llm.ainvoke(messages)
            summary_text = response.content.strip()

            logger.info(f"Successfully generated summary for {target_date}")

            return {
                "success": True,
                "summary": summary_text,
                "data": day_data,
                "progress": progress,
                "error": None
            }

        except Exception as e:
            logger.error(f"Error generating daily summary: {e}", exc_info=True)
            return {
                "success": False,
                "summary": None,
                "data": {},
                "error": str(e)
            }

    def _format_data_for_llm(self, day_data: Dict[str, Any], progress: Dict[str, Any]) -> str:
        """Format day data and progress into a readable string for LLM.

        Args:
            day_data: Day data from get_day_data()
            progress: Progress data from calculate_progress()

        Returns:
            Formatted string with all relevant data
        """
        lines = [
            f"Date: {day_data['date']}",
            "",
            "=== NUTRITION ===",
            f"Calories: {day_data['nutrition']['calories']} kcal",
            f"Protein: {day_data['nutrition']['protein']}g",
            f"Carbs: {day_data['nutrition']['carbs']}g",
            f"Fat: {day_data['nutrition']['fat']}g",
        ]

        # Add progress if available
        if progress.get("has_progress"):
            lines.extend([
                "",
                "=== PROGRESS TOWARDS GOALS ===",
                f"Calories: {progress['calories']['percentage']}% of goal",
                f"Protein: {progress['protein']['percentage']}% of goal",
                f"Carbs: {progress['carbs']['percentage']}% of goal",
                f"Fat: {progress['fat']['percentage']}% of goal",
                f"Water: {progress['water']['percentage']}% of goal",
            ])

        # Add meals
        if day_data.get("meals"):
            lines.extend([
                "",
                "=== MEALS ===",
            ])
            for meal in day_data["meals"]:
                meal_line = f"{meal['category'].title()}"
                if meal['time']:
                    meal_line += f" at {meal['time']}"
                meal_line += f": {meal['calories']} kcal (P: {meal['protein']}g, C: {meal['carbs']}g, F: {meal['fat']}g)"
                lines.append(meal_line)
                if meal.get('notes'):
                    lines.append(f"  Notes: {meal['notes']}")

        # Add exercises
        if day_data.get("exercises"):
            lines.extend([
                "",
                "=== EXERCISES ===",
            ])
            for exercise in day_data["exercises"]:
                ex_line = f"{exercise['name']} ({exercise['type']})"
                if exercise.get('duration_minutes'):
                    ex_line += f" - {exercise['duration_minutes']} min"
                if exercise.get('calories_burned'):
                    ex_line += f" - {exercise['calories_burned']} kcal burned"
                lines.append(ex_line)
        else:
            lines.extend([
                "",
                "=== EXERCISES ===",
                "No exercises logged"
            ])

        # Add wellness data
        lines.extend([
            "",
            "=== WELLNESS ===",
            f"Water: {day_data['water_ml']}ml",
        ])

        if day_data['sleep']['hours'] > 0:
            sleep_line = f"Sleep: {day_data['sleep']['hours']} hours"
            if day_data['sleep'].get('quality'):
                sleep_line += f" (Quality: {day_data['sleep']['quality']})"
            lines.append(sleep_line)

        if day_data['mood'].get('level'):
            mood_line = f"Mood: {day_data['mood']['level']}"
            if day_data['mood'].get('notes'):
                mood_line += f" - {day_data['mood']['notes']}"
            lines.append(mood_line)

        if day_data.get('notes'):
            lines.extend([
                "",
                "=== NOTES ===",
                day_data['notes']
            ])

        return "\n".join(lines)
