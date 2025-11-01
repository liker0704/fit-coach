"""LLM service for multi-provider AI support."""

from typing import Any, Dict, Optional

from langchain.schema import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

from app.config import settings


class LLMService:
    """Service for LLM operations with multi-provider support."""

    _llm_instance: Optional[Any] = None

    @classmethod
    def get_llm(cls) -> Any:
        """Get configured LLM instance based on environment settings.

        Returns:
            LLM instance (ChatOpenAI or ChatGoogleGenerativeAI)

        Raises:
            ValueError: If provider is invalid or API key is missing
        """
        if cls._llm_instance is not None:
            return cls._llm_instance

        provider = settings.LLM_PROVIDER.lower()

        if provider == "openai":
            if not settings.OPENAI_API_KEY:
                raise ValueError(
                    "OPENAI_API_KEY is required when using OpenAI provider. "
                    "Please set it in your .env file."
                )

            cls._llm_instance = ChatOpenAI(
                model=settings.LLM_MODEL_NAME,
                temperature=settings.LLM_TEMPERATURE,
                max_tokens=settings.LLM_MAX_TOKENS,
                api_key=settings.OPENAI_API_KEY,
            )

        elif provider == "gemini":
            if not settings.GOOGLE_API_KEY:
                raise ValueError(
                    "GOOGLE_API_KEY is required when using Gemini provider. "
                    "Please set it in your .env file."
                )

            cls._llm_instance = ChatGoogleGenerativeAI(
                model=settings.LLM_MODEL_NAME,
                temperature=settings.LLM_TEMPERATURE,
                max_output_tokens=settings.LLM_MAX_TOKENS,
                google_api_key=settings.GOOGLE_API_KEY,
                convert_system_message_to_human=True,  # Gemini doesn't support SystemMessage
            )

        else:
            raise ValueError(
                f"Invalid LLM_PROVIDER: '{provider}'. "
                f"Supported providers are: 'openai', 'gemini'"
            )

        return cls._llm_instance

    @classmethod
    def reset_llm(cls) -> None:
        """Reset the LLM instance (useful for testing or switching providers)."""
        cls._llm_instance = None

    @staticmethod
    def generate_coaching_advice(user_data: Dict[str, Any], context: str) -> str:
        """Generate personalized coaching advice based on user data and context.

        Args:
            user_data: Dictionary containing user profile and health data
                Expected keys: full_name, age, weight, target_weight, goals, etc.
            context: Additional context about what type of advice is needed
                Examples: "morning motivation", "exercise recommendation", "nutrition tips"

        Returns:
            Generated coaching advice as a string

        Raises:
            ValueError: If LLM configuration is invalid
            Exception: If LLM generation fails
        """
        llm = LLMService.get_llm()

        # Build system prompt for coaching context
        system_prompt = (
            "You are a professional health and fitness coach. "
            "Provide personalized, encouraging, and actionable advice. "
            "Be supportive and motivating while staying realistic and evidence-based. "
            "Keep responses concise and focused."
        )

        # Build user prompt with context and data
        user_prompt = f"Context: {context}\n\n"
        user_prompt += "User Profile:\n"

        if user_data.get("full_name"):
            user_prompt += f"- Name: {user_data['full_name']}\n"
        if user_data.get("age"):
            user_prompt += f"- Age: {user_data['age']}\n"
        if user_data.get("weight"):
            user_prompt += f"- Current Weight: {user_data['weight']} kg\n"
        if user_data.get("target_weight"):
            user_prompt += f"- Target Weight: {user_data['target_weight']} kg\n"
        if user_data.get("height"):
            user_prompt += f"- Height: {user_data['height']} cm\n"
        if user_data.get("goals"):
            user_prompt += f"- Goals: {', '.join(user_data['goals'])}\n"

        user_prompt += "\nPlease provide personalized coaching advice."

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]

        try:
            response = llm.invoke(messages)
            return response.content
        except Exception as e:
            raise Exception(f"Failed to generate coaching advice: {str(e)}")

    @staticmethod
    def generate_summary(data: Dict[str, Any], period: str) -> str:
        """Generate a summary of health tracking data for a given period.

        Args:
            data: Dictionary containing aggregated health data
                Expected keys: steps, calories, water, sleep, mood, exercises, meals, etc.
            period: Time period for the summary
                Options: "daily", "weekly", "monthly"

        Returns:
            Generated summary as a string

        Raises:
            ValueError: If LLM configuration is invalid or period is invalid
            Exception: If LLM generation fails
        """
        if period not in ["daily", "weekly", "monthly"]:
            raise ValueError(
                f"Invalid period: '{period}'. Must be 'daily', 'weekly', or 'monthly'"
            )

        llm = LLMService.get_llm()

        # Build system prompt for summary generation
        system_prompt = (
            f"You are a health and fitness analyst. "
            f"Generate a clear, insightful {period} summary of the user's health data. "
            f"Highlight achievements, identify patterns, and provide constructive observations. "
            f"Be encouraging and focus on progress. Keep the summary concise and well-structured."
        )

        # Build user prompt with data
        user_prompt = f"{period.capitalize()} Health Data Summary:\n\n"

        if data.get("steps") is not None:
            user_prompt += f"- Steps: {data['steps']}\n"
        if data.get("calories") is not None:
            user_prompt += f"- Calories: {data['calories']}\n"
        if data.get("water") is not None:
            user_prompt += f"- Water: {data['water']} L\n"
        if data.get("sleep") is not None:
            user_prompt += f"- Sleep: {data['sleep']} hours\n"
        if data.get("mood") is not None:
            user_prompt += f"- Average Mood: {data['mood']}/5\n"
        if data.get("exercise_count") is not None:
            user_prompt += f"- Exercise Sessions: {data['exercise_count']}\n"
        if data.get("meal_count") is not None:
            user_prompt += f"- Meals Logged: {data['meal_count']}\n"
        if data.get("weight") is not None:
            user_prompt += f"- Weight: {data['weight']} kg\n"

        if data.get("goals_met"):
            user_prompt += f"\nGoals Met: {', '.join(data['goals_met'])}\n"
        if data.get("goals_missed"):
            user_prompt += f"Goals Missed: {', '.join(data['goals_missed'])}\n"

        user_prompt += f"\nPlease generate an insightful {period} summary."

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]

        try:
            response = llm.invoke(messages)
            return response.content
        except Exception as e:
            raise Exception(f"Failed to generate {period} summary: {str(e)}")
