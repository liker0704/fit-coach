"""General chatbot agent for conversational interactions."""

import logging
from pathlib import Path
from typing import Any, Dict, List

from langchain.chat_models import init_chat_model
from sqlalchemy.orm import Session

from app.agents.base import BaseAgent
from app.config import settings

logger = logging.getLogger(__name__)

# Load prompt
PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "chatbot.txt"
try:
    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        SYSTEM_PROMPT = f.read().strip()
except Exception as e:
    logger.error(f"Failed to load chatbot prompt: {e}")
    SYSTEM_PROMPT = "You are a friendly fitness and nutrition assistant."


class ChatbotAgent(BaseAgent):
    """General chatbot agent for conversational interactions.

    This agent handles general fitness and nutrition conversations,
    provides motivation, answers questions, and offers quick tips.
    """

    def __init__(self, db_session: Session, user_id: int):
        """Initialize Chatbot Agent.

        Args:
            db_session: SQLAlchemy database session
            user_id: ID of the user
        """
        super().__init__(db_session, user_id, "chatbot")
        self.llm = init_chat_model(
            model=settings.LLM_MODEL_NAME,
            model_provider=settings.LLM_PROVIDER,
            temperature=settings.LLM_TEMPERATURE,
            max_tokens=settings.LLM_MAX_TOKENS,
        )
        logger.info(f"Chatbot Agent initialized for user {user_id}")

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Chat with the user.

        Args:
            input_data: Dictionary with keys:
                - message (str): User's message
                - conversation_history (list, optional): Previous messages

        Returns:
            Dictionary with response:
                - success (bool): Whether generation succeeded
                - response (str): Bot's response
                - error (str, optional): Error message if failed
        """
        try:
            user_message = input_data.get("message")
            if not user_message:
                return {
                    "success": False,
                    "response": None,
                    "error": "No message provided"
                }

            logger.info(f"Processing chat message for user {self.user_id}")

            # Build conversation history
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]

            # Add conversation history if provided
            conversation_history = input_data.get("conversation_history", [])
            if conversation_history:
                messages.extend(conversation_history)

            # Add current user message
            messages.append({"role": "user", "content": user_message})

            # Generate response
            response = await self.llm.ainvoke(messages)
            response_text = response.content.strip()

            logger.info(f"Successfully generated chat response for user {self.user_id}")

            return {
                "success": True,
                "response": response_text,
                "error": None
            }

        except Exception as e:
            logger.error(f"Error generating chat response: {e}", exc_info=True)
            return {
                "success": False,
                "response": None,
                "error": str(e)
            }
