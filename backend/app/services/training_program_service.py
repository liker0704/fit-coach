"""Training program generation service."""

import json
import logging
from typing import Any, Dict, List, Optional

from langchain.schema import HumanMessage, SystemMessage
from sqlalchemy.orm import Session

from app.models.user import User
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)


class TrainingProgramService:
    """Service for generating personalized training programs."""

    @staticmethod
    def generate_12week_program(
        db: Session,
        user: User,
        goal: str,
        experience_level: str = "beginner",
        days_per_week: int = 3,
        equipment: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Generate a personalized 12-week training program.

        Args:
            db: Database session
            user: User instance
            goal: Training goal (e.g., "weight_loss", "muscle_gain", "endurance", "strength")
            experience_level: Fitness level ("beginner", "intermediate", "advanced")
            days_per_week: Number of training days per week (2-7)
            equipment: Available equipment (e.g., ["dumbbells", "barbell", "bodyweight"])

        Returns:
            Dictionary with training program data:
            {
                "success": bool,
                "program": {
                    "week_1": {
                        "monday": {"exercises": [...], "warm_up": "...", "cool_down": "..."},
                        ...
                    },
                    ...
                },
                "summary": {
                    "goal": str,
                    "duration": "12 weeks",
                    "days_per_week": int,
                    "notes": str
                }
            }

        Raises:
            Exception: If generation fails
        """
        try:
            # Validate inputs
            if days_per_week < 2 or days_per_week > 7:
                days_per_week = 3

            if experience_level not in ["beginner", "intermediate", "advanced"]:
                experience_level = "beginner"

            # Build system prompt
            system_prompt = (
                "You are a certified personal trainer and strength coach. "
                "Generate a detailed, progressive, and personalized 12-week training program. "
                "Provide specific exercises with sets, reps, rest periods, and intensity guidelines. "
                "Include warm-up and cool-down routines. "
                "Ensure progressive overload and periodization for optimal results. "
                "Return the response as a valid JSON object with the following structure:\n"
                "{\n"
                '  "program": {\n'
                '    "week_1": {\n'
                '      "monday": {\n'
                '        "warm_up": "5 min cardio + dynamic stretching",\n'
                '        "exercises": [\n'
                '          {"name": "Squat", "sets": 3, "reps": 10, "rest": "90s", "notes": "..."},\n'
                '          ...\n'
                '        ],\n'
                '        "cool_down": "5 min stretching"\n'
                '      },\n'
                '      ...\n'
                '    },\n'
                '    "week_2": {...},\n'
                '    ...\n'
                '  },\n'
                '  "summary": {\n'
                '    "goal": "...",\n'
                '    "duration": "12 weeks",\n'
                '    "days_per_week": 3,\n'
                '    "progression_notes": "...",\n'
                '    "notes": "..."\n'
                '  }\n'
                "}"
            )

            # Build user prompt
            user_prompt = f"Create a 12-week training program for:\n\n"
            user_prompt += f"User Profile:\n"
            user_prompt += f"- Age: {user.age or 'N/A'}\n"
            user_prompt += f"- Current Weight: {user.weight or 'N/A'} kg\n"
            user_prompt += f"- Target Weight: {user.target_weight or 'N/A'} kg\n"
            user_prompt += f"- Height: {user.height or 'N/A'} cm\n"
            user_prompt += f"- Experience Level: {experience_level}\n"
            user_prompt += f"- Training Days per Week: {days_per_week}\n"
            user_prompt += f"- Primary Goal: {goal}\n"

            if user.goals:
                user_prompt += f"- Additional Goals: {', '.join(user.goals)}\n"

            if equipment:
                user_prompt += f"- Available Equipment: {', '.join(equipment)}\n"
            else:
                user_prompt += f"- Available Equipment: Bodyweight only\n"

            user_prompt += "\nGenerate a complete 12-week progressive training program with specific exercises, sets, reps, and detailed instructions."

            llm = LLMService.get_llm()
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt),
            ]

            response = llm.invoke(messages)

            # Parse JSON response
            try:
                # Clean up response content
                content = response.content.strip()
                if content.startswith("```json"):
                    content = content[7:]
                if content.startswith("```"):
                    content = content[3:]
                if content.endswith("```"):
                    content = content[:-3]
                content = content.strip()

                program_data = json.loads(content)

                return {
                    "success": True,
                    "program": program_data.get("program", {}),
                    "summary": program_data.get("summary", {}),
                    "goal": goal,
                    "experience_level": experience_level,
                    "days_per_week": days_per_week,
                }
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse training program JSON: {e}")
                # Return raw response if parsing fails
                return {
                    "success": True,
                    "program": {},
                    "summary": {},
                    "raw_response": response.content,
                    "goal": goal,
                    "error": "JSON parsing failed, returning raw response"
                }

        except Exception as e:
            logger.error(f"Failed to generate training program: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    async def stream_program_generation(
        db: Session,
        user: User,
        goal: str,
        experience_level: str = "beginner",
        days_per_week: int = 3,
        equipment: Optional[List[str]] = None,
    ):
        """Stream training program generation in real-time.

        Args:
            db: Database session
            user: User instance
            goal: Training goal
            experience_level: Fitness level
            days_per_week: Training days per week
            equipment: Available equipment

        Yields:
            Chunks of the training program as it's generated
        """
        # Validate inputs
        if days_per_week < 2 or days_per_week > 7:
            days_per_week = 3

        if experience_level not in ["beginner", "intermediate", "advanced"]:
            experience_level = "beginner"

        # Build system prompt (same as non-streaming)
        system_prompt = (
            "You are a certified personal trainer and strength coach. "
            "Generate a detailed, progressive, and personalized 12-week training program. "
            "Provide specific exercises with sets, reps, rest periods, and intensity guidelines. "
            "Include warm-up and cool-down routines. "
            "Ensure progressive overload and periodization for optimal results."
        )

        # Build user prompt
        user_prompt = f"Create a 12-week training program for:\n\n"
        user_prompt += f"User Profile:\n"
        user_prompt += f"- Age: {user.age or 'N/A'}\n"
        user_prompt += f"- Current Weight: {user.weight or 'N/A'} kg\n"
        user_prompt += f"- Target Weight: {user.target_weight or 'N/A'} kg\n"
        user_prompt += f"- Height: {user.height or 'N/A'} cm\n"
        user_prompt += f"- Experience Level: {experience_level}\n"
        user_prompt += f"- Training Days per Week: {days_per_week}\n"
        user_prompt += f"- Primary Goal: {goal}\n"

        if user.goals:
            user_prompt += f"- Additional Goals: {', '.join(user.goals)}\n"

        if equipment:
            user_prompt += f"- Available Equipment: {', '.join(equipment)}\n"
        else:
            user_prompt += f"- Available Equipment: Bodyweight only\n"

        user_prompt += "\nGenerate a complete 12-week progressive training program."

        llm = LLMService.get_llm()
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]

        # Stream response
        async for chunk in llm.astream(messages):
            if hasattr(chunk, 'content') and chunk.content:
                yield chunk.content
