"""Agent API endpoints."""

import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.agents.agents import (
    ChatbotAgent,
    DailySummaryAgent,
    NutritionCoachAgent,
    WorkoutCoachAgent,
)
from app.core.dependencies import get_current_user, get_db
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter()


# ===== Request/Response Schemas =====

class DailySummaryRequest(BaseModel):
    """Request schema for daily summary generation."""
    date: Optional[str] = None  # ISO format, defaults to today


class DailySummaryResponse(BaseModel):
    """Response schema for daily summary."""
    success: bool
    summary: Optional[str] = None
    date: Optional[str] = None
    error: Optional[str] = None


class ChatRequest(BaseModel):
    """Request schema for chatbot."""
    message: str
    conversation_history: Optional[list] = None


class ChatResponse(BaseModel):
    """Response schema for chatbot."""
    success: bool
    response: Optional[str] = None
    error: Optional[str] = None


class CoachRequest(BaseModel):
    """Request schema for nutrition/workout coach."""
    question: str
    date: Optional[str] = None  # ISO format, defaults to today
    conversation_history: Optional[list] = None


class CoachResponse(BaseModel):
    """Response schema for nutrition/workout coach."""
    success: bool
    response: Optional[str] = None
    context_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# ===== Daily Summary Endpoints =====

@router.post("/daily-summary", response_model=DailySummaryResponse)
async def generate_daily_summary(
    request: DailySummaryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate a personalized daily summary.

    Analyzes user's daily activity (meals, exercises, sleep, etc.) and
    generates a comprehensive summary with insights and recommendations.

    Args:
        request: Daily summary request with optional date
        db: Database session
        current_user: Current authenticated user

    Returns:
        DailySummaryResponse with generated summary

    Raises:
        HTTPException: 500 if generation fails
    """
    try:
        logger.info(f"Generating daily summary for user {current_user.id}")

        # Initialize agent
        agent = DailySummaryAgent(db, current_user.id)

        # Execute agent
        result = await agent.execute({"date": request.date})

        if not result["success"]:
            return DailySummaryResponse(
                success=False,
                summary=None,
                error=result.get("error", "Failed to generate summary")
            )

        return DailySummaryResponse(
            success=True,
            summary=result["summary"],
            date=result.get("data", {}).get("date"),
            error=None
        )

    except Exception as e:
        logger.error(f"Error generating daily summary: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate daily summary: {str(e)}"
        )


# ===== Chatbot Endpoints =====

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Chat with the fitness assistant.

    Provides conversational AI support for fitness and nutrition questions,
    motivation, and quick tips.

    Args:
        request: Chat request with message and optional history
        db: Database session
        current_user: Current authenticated user

    Returns:
        ChatResponse with bot's response

    Raises:
        HTTPException: 400 if message is empty, 500 if chat fails
    """
    if not request.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty"
        )

    try:
        logger.info(f"Processing chat message for user {current_user.id}")

        # Initialize agent
        agent = ChatbotAgent(db, current_user.id)

        # Execute agent
        result = await agent.execute({
            "message": request.message,
            "conversation_history": request.conversation_history or []
        })

        if not result["success"]:
            return ChatResponse(
                success=False,
                response=None,
                error=result.get("error", "Failed to generate response")
            )

        return ChatResponse(
            success=True,
            response=result["response"],
            error=None
        )

    except Exception as e:
        logger.error(f"Error processing chat: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process chat: {str(e)}"
        )


# ===== Nutrition Coach Endpoints =====

@router.post("/nutrition-coach", response_model=CoachResponse)
async def nutrition_coach(
    request: CoachRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get nutrition coaching advice.

    Analyzes user's nutrition data and provides personalized dietary
    guidance, meal suggestions, and answers to nutrition questions.

    Args:
        request: Coach request with question and optional date/history
        db: Database session
        current_user: Current authenticated user

    Returns:
        CoachResponse with nutrition advice

    Raises:
        HTTPException: 400 if question is empty, 500 if coaching fails
    """
    if not request.question.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question cannot be empty"
        )

    try:
        logger.info(f"Processing nutrition coaching request for user {current_user.id}")

        # Initialize agent
        agent = NutritionCoachAgent(db, current_user.id)

        # Execute agent
        result = await agent.execute({
            "question": request.question,
            "date": request.date,
            "conversation_history": request.conversation_history or []
        })

        if not result["success"]:
            return CoachResponse(
                success=False,
                response=None,
                error=result.get("error", "Failed to generate response")
            )

        return CoachResponse(
            success=True,
            response=result["response"],
            context_data=result.get("context_data"),
            error=None
        )

    except Exception as e:
        logger.error(f"Error processing nutrition coaching: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process nutrition coaching: {str(e)}"
        )


# ===== Workout Coach Endpoints =====

@router.post("/workout-coach", response_model=CoachResponse)
async def workout_coach(
    request: CoachRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get workout coaching advice.

    Analyzes user's workout data and provides personalized fitness
    guidance, workout plans, and answers to exercise questions.

    Args:
        request: Coach request with question and optional date/history
        db: Database session
        current_user: Current authenticated user

    Returns:
        CoachResponse with workout advice

    Raises:
        HTTPException: 400 if question is empty, 500 if coaching fails
    """
    if not request.question.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question cannot be empty"
        )

    try:
        logger.info(f"Processing workout coaching request for user {current_user.id}")

        # Initialize agent
        agent = WorkoutCoachAgent(db, current_user.id)

        # Execute agent
        result = await agent.execute({
            "question": request.question,
            "date": request.date,
            "conversation_history": request.conversation_history or []
        })

        if not result["success"]:
            return CoachResponse(
                success=False,
                response=None,
                error=result.get("error", "Failed to generate response")
            )

        return CoachResponse(
            success=True,
            response=result["response"],
            context_data=result.get("context_data"),
            error=None
        )

    except Exception as e:
        logger.error(f"Error processing workout coaching: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process workout coaching: {str(e)}"
        )
