"""Voice API endpoints for Speech-to-Text and Text-to-Speech."""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import Response, StreamingResponse
from pydantic import BaseModel

from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.voice_service import VoiceService

logger = logging.getLogger(__name__)

router = APIRouter()


# ===== Request/Response Schemas =====

class TranscriptionResponse(BaseModel):
    """Response schema for speech-to-text."""
    success: bool
    text: str
    language: Optional[str] = None
    error: Optional[str] = None


class TTSRequest(BaseModel):
    """Request schema for text-to-speech."""
    text: str
    voice: Optional[str] = "alloy"  # alloy, echo, fable, onyx, nova, shimmer
    speed: Optional[float] = 1.0


class TTSResponse(BaseModel):
    """Response schema for text-to-speech."""
    success: bool
    audio_base64: Optional[str] = None
    format: str = "mp3"
    error: Optional[str] = None


# ===== Speech-to-Text Endpoints =====

@router.post("/speech-to-text", response_model=TranscriptionResponse)
async def speech_to_text(
    audio: UploadFile = File(...),
    language: str = Form(default="en"),
    current_user: User = Depends(get_current_user),
):
    """Convert speech audio to text.

    Args:
        audio: Audio file (webm, mp3, wav, etc.)
        language: Language code (en, ru, cz)
        current_user: Current authenticated user

    Returns:
        TranscriptionResponse with transcribed text

    Raises:
        HTTPException: 400 if audio format invalid, 500 if transcription fails
    """
    try:
        logger.info(f"Speech-to-text request from user {current_user.id}")

        # Read audio file
        audio_data = await audio.read()

        if len(audio_data) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty audio file"
            )

        # Get audio format from filename
        audio_format = "webm"
        if audio.filename:
            extension = audio.filename.split(".")[-1].lower()
            if extension in ["mp3", "wav", "m4a", "webm", "ogg"]:
                audio_format = extension

        # Transcribe
        result = VoiceService.speech_to_text(
            audio_data=audio_data,
            audio_format=audio_format,
            language=language
        )

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Transcription failed")
            )

        return TranscriptionResponse(
            success=True,
            text=result["text"],
            language=result.get("language"),
            error=None
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in speech-to-text endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to transcribe audio: {str(e)}"
        )


# ===== Text-to-Speech Endpoints =====

@router.post("/text-to-speech", response_model=TTSResponse)
async def text_to_speech(
    request: TTSRequest,
    current_user: User = Depends(get_current_user),
):
    """Convert text to speech audio.

    Args:
        request: TTS request with text and voice options
        current_user: Current authenticated user

    Returns:
        TTSResponse with base64-encoded audio

    Raises:
        HTTPException: 400 if text empty, 500 if TTS fails
    """
    try:
        logger.info(f"Text-to-speech request from user {current_user.id}")

        if not request.text or len(request.text.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Text cannot be empty"
            )

        # Generate speech
        result = VoiceService.text_to_speech(
            text=request.text,
            voice=request.voice,
            speed=request.speed
        )

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "TTS failed")
            )

        # Encode audio as base64
        import base64
        audio_base64 = base64.b64encode(result["audio_data"]).decode("utf-8")

        return TTSResponse(
            success=True,
            audio_base64=audio_base64,
            format=result["format"],
            error=None
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in text-to-speech endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate speech: {str(e)}"
        )


@router.post("/text-to-speech/stream")
async def text_to_speech_stream(
    request: TTSRequest,
    current_user: User = Depends(get_current_user),
):
    """Stream text-to-speech audio.

    Args:
        request: TTS request
        current_user: Current authenticated user

    Returns:
        StreamingResponse with audio/mpeg content

    Raises:
        HTTPException: 400 if text empty
    """
    try:
        logger.info(f"TTS stream request from user {current_user.id}")

        if not request.text or len(request.text.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Text cannot be empty"
            )

        def generate_audio():
            """Generate audio stream."""
            try:
                for chunk in VoiceService.text_to_speech_stream(
                    text=request.text,
                    voice=request.voice,
                    speed=request.speed
                ):
                    yield chunk
            except Exception as e:
                logger.error(f"Error in TTS stream: {e}", exc_info=True)

        return StreamingResponse(
            generate_audio(),
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": 'inline; filename="speech.mp3"'
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in TTS stream endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stream speech: {str(e)}"
        )


@router.post("/text-to-speech/audio")
async def text_to_speech_audio(
    request: TTSRequest,
    current_user: User = Depends(get_current_user),
):
    """Generate speech audio and return as direct audio response.

    Args:
        request: TTS request
        current_user: Current authenticated user

    Returns:
        Direct audio response (audio/mpeg)

    Raises:
        HTTPException: 400 if text empty, 500 if TTS fails
    """
    try:
        logger.info(f"TTS audio request from user {current_user.id}")

        if not request.text or len(request.text.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Text cannot be empty"
            )

        # Generate speech
        result = VoiceService.text_to_speech(
            text=request.text,
            voice=request.voice,
            speed=request.speed
        )

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "TTS failed")
            )

        # Return audio directly
        return Response(
            content=result["audio_data"],
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": 'inline; filename="speech.mp3"'
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in TTS audio endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate speech audio: {str(e)}"
        )
