"""Voice service for Speech-to-Text and Text-to-Speech."""

import base64
import logging
from typing import Optional

from app.config import settings

logger = logging.getLogger(__name__)


class VoiceService:
    """Service for voice processing (STT and TTS)."""

    @staticmethod
    def speech_to_text(
        audio_data: bytes,
        audio_format: str = "webm",
        language: str = "en"
    ) -> dict:
        """Convert speech audio to text using OpenAI Whisper API.

        Args:
            audio_data: Audio file bytes
            audio_format: Audio format (webm, mp3, wav, etc.)
            language: Language code (en, ru, cz, etc.)

        Returns:
            Dictionary with transcription result:
            {
                "success": bool,
                "text": str,
                "language": str,
                "error": Optional[str]
            }
        """
        try:
            if not settings.OPENAI_API_KEY:
                return {
                    "success": False,
                    "text": "",
                    "error": "OpenAI API key not configured"
                }

            # Import OpenAI client
            from openai import OpenAI
            client = OpenAI(api_key=settings.OPENAI_API_KEY)

            # Create a temporary file-like object
            import io
            audio_file = io.BytesIO(audio_data)
            audio_file.name = f"audio.{audio_format}"

            # Transcribe using Whisper
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=language
            )

            return {
                "success": True,
                "text": transcript.text,
                "language": language,
                "error": None
            }

        except Exception as e:
            logger.error(f"Error in speech-to-text: {e}", exc_info=True)
            return {
                "success": False,
                "text": "",
                "error": str(e)
            }

    @staticmethod
    def text_to_speech(
        text: str,
        voice: str = "alloy",
        speed: float = 1.0
    ) -> dict:
        """Convert text to speech audio using OpenAI TTS API.

        Args:
            text: Text to convert to speech
            voice: Voice name (alloy, echo, fable, onyx, nova, shimmer)
            speed: Speech speed (0.25 to 4.0)

        Returns:
            Dictionary with audio result:
            {
                "success": bool,
                "audio_data": bytes (MP3 audio),
                "format": "mp3",
                "error": Optional[str]
            }
        """
        try:
            if not settings.OPENAI_API_KEY:
                return {
                    "success": False,
                    "audio_data": b"",
                    "format": "mp3",
                    "error": "OpenAI API key not configured"
                }

            # Import OpenAI client
            from openai import OpenAI
            client = OpenAI(api_key=settings.OPENAI_API_KEY)

            # Generate speech
            response = client.audio.speech.create(
                model="tts-1",  # or "tts-1-hd" for higher quality
                voice=voice,
                input=text,
                speed=speed
            )

            # Get audio data
            audio_data = response.content

            return {
                "success": True,
                "audio_data": audio_data,
                "format": "mp3",
                "error": None
            }

        except Exception as e:
            logger.error(f"Error in text-to-speech: {e}", exc_info=True)
            return {
                "success": False,
                "audio_data": b"",
                "format": "mp3",
                "error": str(e)
            }

    @staticmethod
    def text_to_speech_stream(
        text: str,
        voice: str = "alloy",
        speed: float = 1.0
    ):
        """Stream text-to-speech audio in real-time.

        Args:
            text: Text to convert to speech
            voice: Voice name
            speed: Speech speed

        Yields:
            Audio chunks as bytes
        """
        try:
            if not settings.OPENAI_API_KEY:
                logger.error("OpenAI API key not configured for TTS streaming")
                return

            # Import OpenAI client
            from openai import OpenAI
            client = OpenAI(api_key=settings.OPENAI_API_KEY)

            # Stream speech generation
            response = client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text,
                speed=speed
            )

            # Stream audio data
            # Note: OpenAI TTS doesn't support streaming yet, so we return full audio
            # For real streaming, would need to use Google Cloud TTS or similar
            yield response.content

        except Exception as e:
            logger.error(f"Error in TTS streaming: {e}", exc_info=True)
            return
