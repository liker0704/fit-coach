"""Meal plan generation service."""

import json
import logging
from typing import Any, Dict, List, Optional

from langchain.schema import HumanMessage, SystemMessage
from sqlalchemy.orm import Session

from app.models.user import User
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)


class MealPlanService:
    """Service for generating personalized meal plans."""

    @staticmethod
    def generate_7day_meal_plan(
        db: Session,
        user: User,
        dietary_preferences: Optional[List[str]] = None,
        calorie_target: Optional[int] = None,
        allergies: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Generate a personalized 7-day meal plan.

        Args:
            db: Database session
            user: User instance
            dietary_preferences: List of dietary preferences (e.g., "vegetarian", "keto", "paleo")
            calorie_target: Daily calorie target (if None, calculated from user data)
            allergies: List of food allergies/restrictions

        Returns:
            Dictionary with meal plan data:
            {
                "success": bool,
                "meal_plan": {
                    "monday": {"breakfast": {...}, "lunch": {...}, "dinner": {...}, "snacks": [...]},
                    "tuesday": {...},
                    ...
                },
                "summary": {
                    "daily_calories": int,
                    "macros": {"protein": int, "carbs": int, "fats": int},
                    "notes": str
                }
            }

        Raises:
            Exception: If generation fails
        """
        try:
            # Calculate calorie target if not provided
            if not calorie_target:
                calorie_target = MealPlanService._calculate_calorie_target(user)

            # Build system prompt
            system_prompt = (
                "You are a professional nutritionist and meal planner. "
                "Generate a detailed, balanced, and personalized 7-day meal plan. "
                "Provide specific meals with ingredients, portions, and estimated macronutrients. "
                "Make the plan practical, delicious, and aligned with the user's goals. "
                "Return the response as a valid JSON object with the following structure:\n"
                "{\n"
                '  "meal_plan": {\n'
                '    "monday": {\n'
                '      "breakfast": {"name": "...", "calories": 400, "protein": 20, "carbs": 45, "fats": 12, "ingredients": [...]},\n'
                '      "lunch": {...},\n'
                '      "dinner": {...},\n'
                '      "snacks": [{...}]\n'
                '    },\n'
                '    "tuesday": {...},\n'
                '    ...\n'
                '  },\n'
                '  "summary": {\n'
                '    "daily_calories": 2000,\n'
                '    "macros": {"protein": 150, "carbs": 200, "fats": 65},\n'
                '    "notes": "..."\n'
                '  }\n'
                "}"
            )

            # Build user prompt
            user_prompt = f"Create a 7-day meal plan for:\n\n"
            user_prompt += f"User Profile:\n"
            user_prompt += f"- Age: {user.age or 'N/A'}\n"
            user_prompt += f"- Current Weight: {user.weight or 'N/A'} kg\n"
            user_prompt += f"- Target Weight: {user.target_weight or 'N/A'} kg\n"
            user_prompt += f"- Height: {user.height or 'N/A'} cm\n"
            user_prompt += f"- Daily Calorie Target: {calorie_target} kcal\n"

            if user.goals:
                user_prompt += f"- Goals: {', '.join(user.goals)}\n"

            if dietary_preferences:
                user_prompt += f"- Dietary Preferences: {', '.join(dietary_preferences)}\n"

            if allergies:
                user_prompt += f"- Allergies/Restrictions: {', '.join(allergies)}\n"

            user_prompt += "\nGenerate a complete 7-day meal plan with breakfast, lunch, dinner, and snacks for each day."

            llm = LLMService.get_llm()
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt),
            ]

            response = llm.invoke(messages)

            # Parse JSON response
            try:
                # Clean up response content (remove markdown code blocks if present)
                content = response.content.strip()
                if content.startswith("```json"):
                    content = content[7:]  # Remove ```json
                if content.startswith("```"):
                    content = content[3:]   # Remove ```
                if content.endswith("```"):
                    content = content[:-3]  # Remove trailing ```
                content = content.strip()

                meal_plan_data = json.loads(content)

                return {
                    "success": True,
                    "meal_plan": meal_plan_data.get("meal_plan", {}),
                    "summary": meal_plan_data.get("summary", {}),
                    "calorie_target": calorie_target,
                }
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse meal plan JSON: {e}")
                # Return raw response if parsing fails
                return {
                    "success": True,
                    "meal_plan": {},
                    "summary": {},
                    "raw_response": response.content,
                    "calorie_target": calorie_target,
                    "error": "JSON parsing failed, returning raw response"
                }

        except Exception as e:
            logger.error(f"Failed to generate meal plan: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    def _calculate_calorie_target(user: User) -> int:
        """Calculate daily calorie target based on user data.

        Uses Mifflin-St Jeor Equation with activity multiplier.

        Args:
            user: User instance

        Returns:
            Estimated daily calorie target
        """
        # Default if insufficient data
        if not user.weight or not user.height or not user.age:
            return 2000  # Average adult target

        # Mifflin-St Jeor Equation (assuming male, can be adjusted)
        # BMR = 10 * weight(kg) + 6.25 * height(cm) - 5 * age(y) + 5 (male) or -161 (female)
        # For simplicity, using male formula (can add gender field later)
        bmr = 10 * user.weight + 6.25 * user.height - 5 * user.age + 5

        # Activity multiplier (assuming moderate activity: 1.55)
        activity_multiplier = 1.55
        tdee = bmr * activity_multiplier

        # Adjust based on goal
        if user.target_weight:
            if user.target_weight < user.weight:
                # Weight loss: -500 kcal/day (lose ~0.5 kg/week)
                return int(tdee - 500)
            elif user.target_weight > user.weight:
                # Weight gain: +300 kcal/day
                return int(tdee + 300)

        # Maintenance
        return int(tdee)

    @staticmethod
    async def stream_meal_plan_generation(
        db: Session,
        user: User,
        dietary_preferences: Optional[List[str]] = None,
        calorie_target: Optional[int] = None,
        allergies: Optional[List[str]] = None,
    ):
        """Stream meal plan generation in real-time.

        Args:
            db: Database session
            user: User instance
            dietary_preferences: List of dietary preferences
            calorie_target: Daily calorie target
            allergies: List of food allergies

        Yields:
            Chunks of the meal plan as it's generated
        """
        # Calculate calorie target if not provided
        if not calorie_target:
            calorie_target = MealPlanService._calculate_calorie_target(user)

        # Build system prompt (same as non-streaming)
        system_prompt = (
            "You are a professional nutritionist and meal planner. "
            "Generate a detailed, balanced, and personalized 7-day meal plan. "
            "Provide specific meals with ingredients, portions, and estimated macronutrients. "
            "Make the plan practical, delicious, and aligned with the user's goals."
        )

        # Build user prompt
        user_prompt = f"Create a 7-day meal plan for:\n\n"
        user_prompt += f"User Profile:\n"
        user_prompt += f"- Age: {user.age or 'N/A'}\n"
        user_prompt += f"- Current Weight: {user.weight or 'N/A'} kg\n"
        user_prompt += f"- Target Weight: {user.target_weight or 'N/A'} kg\n"
        user_prompt += f"- Height: {user.height or 'N/A'} cm\n"
        user_prompt += f"- Daily Calorie Target: {calorie_target} kcal\n"

        if user.goals:
            user_prompt += f"- Goals: {', '.join(user.goals)}\n"

        if dietary_preferences:
            user_prompt += f"- Dietary Preferences: {', '.join(dietary_preferences)}\n"

        if allergies:
            user_prompt += f"- Allergies/Restrictions: {', '.join(allergies)}\n"

        user_prompt += "\nGenerate a complete 7-day meal plan with breakfast, lunch, dinner, and snacks for each day."

        llm = LLMService.get_llm()
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]

        # Stream response
        async for chunk in llm.astream(messages):
            if hasattr(chunk, 'content') and chunk.content:
                yield chunk.content
