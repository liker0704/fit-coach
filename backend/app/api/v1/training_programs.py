"""Training program API endpoints."""

import logging
from typing import AsyncIterator

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.training_program import TrainingProgram
from app.models.user import User
from app.schemas.training_program import (
    TrainingProgramCreateResponse,
    TrainingProgramGenerateRequest,
    TrainingProgramListResponse,
    TrainingProgramResponse,
)
from app.services.training_program_service import TrainingProgramService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/generate", response_model=TrainingProgramCreateResponse)
async def generate_training_program(
    request: TrainingProgramGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate a new 12-week training program.

    Args:
        request: Training program generation request
        db: Database session
        current_user: Current authenticated user

    Returns:
        TrainingProgramCreateResponse with generated program

    Raises:
        HTTPException: 500 if generation fails
    """
    try:
        logger.info(f"Generating training program for user {current_user.id}")

        # Generate training program
        result = TrainingProgramService.generate_12week_program(
            db=db,
            user=current_user,
            goal=request.goal,
            experience_level=request.experience_level,
            days_per_week=request.days_per_week,
            equipment=request.equipment,
        )

        if not result["success"]:
            return TrainingProgramCreateResponse(
                success=False,
                program=None,
                error=result.get("error", "Failed to generate training program")
            )

        # Save to database
        program = TrainingProgram(
            user_id=current_user.id,
            name=request.name or f"{request.goal.replace('_', ' ').title()} Program",
            description=request.description,
            goal=request.goal,
            experience_level=request.experience_level,
            days_per_week=request.days_per_week,
            equipment=request.equipment,
            program_data=result.get("program", {}),
            summary=result.get("summary", {}),
            is_active=1,
        )

        db.add(program)
        db.commit()
        db.refresh(program)

        logger.info(f"Training program created successfully: ID {program.id}")

        return TrainingProgramCreateResponse(
            success=True,
            program=TrainingProgramResponse.model_validate(program),
            error=None
        )

    except Exception as e:
        logger.error(f"Error generating training program: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate training program: {str(e)}"
        )


@router.get("/", response_model=TrainingProgramListResponse)
async def get_training_programs(
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all training programs for current user.

    Args:
        active_only: Only return active programs (default True)
        db: Database session
        current_user: Current authenticated user

    Returns:
        TrainingProgramListResponse with list of programs
    """
    try:
        query = db.query(TrainingProgram).filter(TrainingProgram.user_id == current_user.id)

        if active_only:
            query = query.filter(TrainingProgram.is_active == 1)

        programs = query.order_by(TrainingProgram.created_at.desc()).all()

        return TrainingProgramListResponse(
            programs=[TrainingProgramResponse.model_validate(p) for p in programs],
            total=len(programs)
        )

    except Exception as e:
        logger.error(f"Error fetching training programs: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch training programs: {str(e)}"
        )


@router.get("/{program_id}", response_model=TrainingProgramResponse)
async def get_training_program(
    program_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific training program by ID.

    Args:
        program_id: Training program ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        TrainingProgramResponse

    Raises:
        HTTPException: 404 if program not found
    """
    try:
        program = db.query(TrainingProgram).filter(
            TrainingProgram.id == program_id,
            TrainingProgram.user_id == current_user.id
        ).first()

        if not program:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Training program not found"
            )

        return TrainingProgramResponse.model_validate(program)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching training program: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch training program: {str(e)}"
        )


@router.delete("/{program_id}")
async def delete_training_program(
    program_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete (archive) a training program.

    Args:
        program_id: Training program ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Success message

    Raises:
        HTTPException: 404 if program not found
    """
    try:
        program = db.query(TrainingProgram).filter(
            TrainingProgram.id == program_id,
            TrainingProgram.user_id == current_user.id
        ).first()

        if not program:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Training program not found"
            )

        # Archive instead of delete
        program.is_active = 0
        db.commit()

        return {"success": True, "message": "Training program archived successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting training program: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete training program: {str(e)}"
        )


@router.post("/generate/stream")
async def stream_program_generation(
    request: TrainingProgramGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Stream training program generation in real-time.

    Args:
        request: Training program generation request
        db: Database session
        current_user: Current authenticated user

    Returns:
        StreamingResponse with SSE format
    """
    try:
        logger.info(f"Streaming training program generation for user {current_user.id}")

        async def generate_stream() -> AsyncIterator[bytes]:
            """Generate SSE stream."""
            try:
                async for chunk in TrainingProgramService.stream_program_generation(
                    db=db,
                    user=current_user,
                    goal=request.goal,
                    experience_level=request.experience_level,
                    days_per_week=request.days_per_week,
                    equipment=request.equipment,
                ):
                    yield f"data: {chunk}\n\n".encode("utf-8")
            except Exception as e:
                logger.error(f"Error in program stream: {e}", exc_info=True)
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
        logger.error(f"Error starting program stream: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stream training program: {str(e)}"
        )
