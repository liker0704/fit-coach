"""Agent API endpoints."""

import logging
from typing import Any, AsyncIterator, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
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
from app.services.llm_service import LLMService
from app.services.agent_coordinator import AgentCoordinator

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


class CoordinationRequest(BaseModel):
    """Request schema for multi-agent coordination."""
    task: str
    agents: list[str]  # e.g., ["nutrition", "workout"]
    context: Optional[Dict[str, Any]] = None


class CoordinationResponse(BaseModel):
    """Response schema for multi-agent coordination."""
    success: bool
    task: Optional[str] = None
    agent_results: Optional[Dict[str, Any]] = None
    synthesis: Optional[str] = None
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


# ===== Streaming Endpoints =====

async def generate_stream(iterator: AsyncIterator[str]) -> AsyncIterator[bytes]:
    """Convert async string iterator to bytes for streaming response.

    Args:
        iterator: Async iterator yielding string chunks

    Yields:
        Bytes chunks for streaming response
    """
    try:
        async for chunk in iterator:
            # Send each chunk as Server-Sent Events (SSE) format
            yield f"data: {chunk}\n\n".encode("utf-8")
    except Exception as e:
        logger.error(f"Error in stream generation: {e}", exc_info=True)
        yield f"data: [ERROR: {str(e)}]\n\n".encode("utf-8")
    finally:
        # Send completion signal
        yield "data: [DONE]\n\n".encode("utf-8")


@router.post("/chat/stream")
async def stream_chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
):
    """Stream chatbot responses in real-time.

    Uses Server-Sent Events (SSE) to stream the response as it's generated.

    Args:
        request: Chat request with message and optional history
        current_user: Current authenticated user

    Returns:
        StreamingResponse with SSE format
    """
    try:
        logger.info(f"Streaming chat for user {current_user.id}")

        # Build context from conversation history
        context = None
        if request.conversation_history:
            context = f"Previous conversation: {len(request.conversation_history)} messages"

        # Get streaming iterator
        stream_iterator = LLMService.stream_chat_response(
            message=request.message,
            context=context
        )

        return StreamingResponse(
            generate_stream(stream_iterator),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",  # Disable nginx buffering
            }
        )

    except Exception as e:
        logger.error(f"Error in stream_chat: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stream chat: {str(e)}"
        )


@router.post("/nutrition-coach/stream")
async def stream_nutrition_coaching(
    request: CoachRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Stream nutrition coaching advice in real-time.

    Args:
        request: Coach request with question and optional date
        db: Database session
        current_user: Current authenticated user

    Returns:
        StreamingResponse with SSE format
    """
    try:
        logger.info(f"Streaming nutrition coaching for user {current_user.id}")

        # Build user data for context
        user_data = {
            "full_name": current_user.full_name,
            "age": current_user.age,
            "weight": current_user.weight,
            "target_weight": current_user.target_weight,
            "height": current_user.height,
            "goals": current_user.goals or [],
        }

        # Build context
        context = f"Nutrition question: {request.question}"

        # Get streaming iterator
        stream_iterator = LLMService.stream_coaching_advice(
            user_data=user_data,
            context=context
        )

        return StreamingResponse(
            generate_stream(stream_iterator),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            }
        )

    except Exception as e:
        logger.error(f"Error in stream_nutrition_coaching: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stream nutrition coaching: {str(e)}"
        )


@router.post("/workout-coach/stream")
async def stream_workout_coaching(
    request: CoachRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Stream workout coaching advice in real-time.

    Args:
        request: Coach request with question and optional date
        db: Database session
        current_user: Current authenticated user

    Returns:
        StreamingResponse with SSE format
    """
    try:
        logger.info(f"Streaming workout coaching for user {current_user.id}")

        # Build user data for context
        user_data = {
            "full_name": current_user.full_name,
            "age": current_user.age,
            "weight": current_user.weight,
            "target_weight": current_user.target_weight,
            "height": current_user.height,
            "goals": current_user.goals or [],
        }

        # Build context
        context = f"Workout question: {request.question}"

        # Get streaming iterator
        stream_iterator = LLMService.stream_coaching_advice(
            user_data=user_data,
            context=context
        )

        return StreamingResponse(
            generate_stream(stream_iterator),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            }
        )

    except Exception as e:
        logger.error(f"Error in stream_workout_coaching: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stream workout coaching: {str(e)}"
        )


# ===== Multi-Agent Coordination Endpoints =====

@router.post("/coordinate", response_model=CoordinationResponse)
async def coordinate_agents(
    request: CoordinationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Coordinate multiple agents to complete a complex task.

    Args:
        request: Coordination request with task and agent list
        db: Database session
        current_user: Current authenticated user

    Returns:
        CoordinationResponse with results from all agents and synthesis

    Example:
        {
            "task": "Create comprehensive health plan",
            "agents": ["nutrition", "workout"],
            "context": {"date": "2024-01-15"}
        }
    """
    try:
        logger.info(f"Coordinating agents for user {current_user.id}")

        result = await AgentCoordinator.coordinate_agents(
            db=db,
            user=current_user,
            task=request.task,
            agents=request.agents,
            context=request.context
        )

        return CoordinationResponse(
            success=result["success"],
            task=result.get("task"),
            agent_results=result.get("agent_results"),
            synthesis=result.get("synthesis"),
            error=result.get("error")
        )

    except Exception as e:
        logger.error(f"Error in agent coordination: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to coordinate agents: {str(e)}"
        )


@router.post("/coordinate/stream")
async def stream_coordinated_response(
    request: CoordinationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Stream coordinated response from multiple agents.

    Args:
        request: Coordination request
        db: Database session
        current_user: Current authenticated user

    Returns:
        StreamingResponse with SSE format
    """
    try:
        logger.info(f"Streaming coordinated response for user {current_user.id}")

        async def generate_stream() -> AsyncIterator[bytes]:
            """Generate SSE stream."""
            try:
                async for chunk in AgentCoordinator.stream_coordinated_response(
                    db=db,
                    user=current_user,
                    task=request.task,
                    agents=request.agents,
                    context=request.context
                ):
                    yield f"data: {chunk}\n\n".encode("utf-8")
            except Exception as e:
                logger.error(f"Error in coordination stream: {e}", exc_info=True)
                yield f"data: [ERROR: {str(e)}]\n\n".encode("utf-8")
            finally:
                yield "data: [DONE]\n\n".encode("utf-8")

        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            }
        )

    except Exception as e:
        logger.error(f"Error starting coordination stream: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stream coordinated response: {str(e)}"
        )
