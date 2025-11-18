"""Integration tests for Voice API endpoints (Speech-to-Text and Text-to-Speech)."""

import httpx
import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock, Mock
import base64
import io
import json

# Base URL for the API
BASE_URL = "http://localhost:8001"
API_V1 = f"{BASE_URL}/api/v1"

# Global test data
_test_user_email = None
_test_user_password = "TestPassword123!"
_test_user_username = None
_access_token = None


def get_or_create_test_user():
    """Get or create test user and return access token."""
    global _test_user_email, _test_user_username, _access_token

    if _access_token:
        return _access_token

    # Create unique username/email for this test session
    timestamp = str(int(datetime.now().timestamp()))
    _test_user_email = f"testvoice{timestamp}@example.com"
    _test_user_username = f"testvoice{timestamp}"

    with httpx.Client() as client:
        # Register
        response = client.post(
            f"{API_V1}/auth/register",
            json={
                "email": _test_user_email,
                "username": _test_user_username,
                "password": _test_user_password,
                "full_name": "Test Voice User"
            }
        )

        # Login to get token
        login_response = client.post(
            f"{API_V1}/auth/login",
            json={
                "email": _test_user_email,
                "password": _test_user_password
            }
        )

        if login_response.status_code == 200:
            _access_token = login_response.json()["access_token"]
            return _access_token

        return None


def get_auth_headers():
    """Get authorization headers with access token."""
    token = get_or_create_test_user()
    return {"Authorization": f"Bearer {token}"}


def create_test_audio_file(format="wav", size=1024):
    """Create a dummy audio file for testing.

    Args:
        format: Audio format extension
        size: Size in bytes

    Returns:
        Tuple of (filename, file_content)
    """
    # Create dummy audio data (not real audio, but enough for testing)
    audio_data = b'\x00' * size
    filename = f"test_audio.{format}"
    return filename, audio_data


class TestSpeechToText:
    """Test suite for Speech-to-Text endpoint."""

    @patch('app.services.voice_service.VoiceService.speech_to_text')
    def test_01_speech_to_text_success(self, mock_stt):
        """Test POST /api/v1/speech-to-text - Successful transcription."""
        # Mock the service response
        mock_stt.return_value = {
            "success": True,
            "text": "Hello, this is a test transcription",
            "language": "en",
            "error": None
        }

        filename, audio_data = create_test_audio_file("webm", 2048)

        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/speech-to-text",
                files={"audio": (filename, audio_data, "audio/webm")},
                data={"language": "en"},
                headers=get_auth_headers(),
                timeout=30.0
            )

            assert response.status_code == 200, f"Failed to transcribe: {response.text}"
            data = response.json()

            assert data["success"] is True
            assert data["text"] == "Hello, this is a test transcription"
            assert data["language"] == "en"
            assert data["error"] is None

            # Verify service was called
            mock_stt.assert_called_once()

            print(f"\nSuccessfully transcribed audio: '{data['text']}'")

    @patch('app.services.voice_service.VoiceService.speech_to_text')
    def test_02_speech_to_text_different_languages(self, mock_stt):
        """Test speech-to-text with different languages."""
        test_languages = [
            ("en", "Hello world"),
            ("ru", "Привет мир"),
            ("cs", "Ahoj světe")
        ]

        for language, expected_text in test_languages:
            mock_stt.return_value = {
                "success": True,
                "text": expected_text,
                "language": language,
                "error": None
            }

            filename, audio_data = create_test_audio_file("mp3")

            with httpx.Client() as client:
                response = client.post(
                    f"{API_V1}/speech-to-text",
                    files={"audio": (filename, audio_data, "audio/mp3")},
                    data={"language": language},
                    headers=get_auth_headers(),
                    timeout=30.0
                )

                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert data["language"] == language
                assert data["text"] == expected_text

            print(f"Tested language {language}: '{expected_text}'")

    @patch('app.services.voice_service.VoiceService.speech_to_text')
    def test_03_speech_to_text_various_formats(self, mock_stt):
        """Test speech-to-text with different audio formats."""
        formats = ["webm", "mp3", "wav", "m4a", "ogg"]

        for audio_format in formats:
            mock_stt.return_value = {
                "success": True,
                "text": f"Test with {audio_format} format",
                "language": "en",
                "error": None
            }

            filename, audio_data = create_test_audio_file(audio_format)

            with httpx.Client() as client:
                response = client.post(
                    f"{API_V1}/speech-to-text",
                    files={"audio": (filename, audio_data, f"audio/{audio_format}")},
                    data={"language": "en"},
                    headers=get_auth_headers(),
                    timeout=30.0
                )

                assert response.status_code == 200, f"Failed for format {audio_format}"
                data = response.json()
                assert data["success"] is True

            print(f"Successfully tested format: {audio_format}")

    def test_04_speech_to_text_empty_file(self):
        """Test speech-to-text with empty audio file."""
        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/speech-to-text",
                files={"audio": ("empty.webm", b"", "audio/webm")},
                data={"language": "en"},
                headers=get_auth_headers(),
                timeout=30.0
            )

            assert response.status_code == 400, "Should reject empty audio file"
            data = response.json()
            assert "empty" in data["detail"].lower() or "empty" in str(data).lower()

            print("\nCorrectly rejected empty audio file")

    def test_05_speech_to_text_missing_audio(self):
        """Test speech-to-text without audio file."""
        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/speech-to-text",
                data={"language": "en"},
                headers=get_auth_headers(),
                timeout=30.0
            )

            assert response.status_code == 422, "Should require audio file"
            print("\nCorrectly rejected request without audio file")

    @patch('app.services.voice_service.VoiceService.speech_to_text')
    def test_06_speech_to_text_service_failure(self, mock_stt):
        """Test handling of service failure."""
        mock_stt.return_value = {
            "success": False,
            "text": "",
            "error": "OpenAI API error"
        }

        filename, audio_data = create_test_audio_file("webm")

        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/speech-to-text",
                files={"audio": (filename, audio_data, "audio/webm")},
                data={"language": "en"},
                headers=get_auth_headers(),
                timeout=30.0
            )

            assert response.status_code == 500, "Should return 500 on service failure"
            print("\nCorrectly handled service failure")

    def test_07_speech_to_text_requires_auth(self):
        """Test that speech-to-text requires authentication."""
        filename, audio_data = create_test_audio_file("webm")

        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/speech-to-text",
                files={"audio": (filename, audio_data, "audio/webm")},
                data={"language": "en"},
                timeout=30.0
            )

            assert response.status_code in [401, 403], "Should require authentication"
            print("\nSpeech-to-text correctly requires authentication")

    @patch('app.services.voice_service.VoiceService.speech_to_text')
    def test_08_speech_to_text_default_language(self, mock_stt):
        """Test speech-to-text with default language (en)."""
        mock_stt.return_value = {
            "success": True,
            "text": "Default language test",
            "language": "en",
            "error": None
        }

        filename, audio_data = create_test_audio_file("webm")

        with httpx.Client() as client:
            # Don't specify language, should default to 'en'
            response = client.post(
                f"{API_V1}/speech-to-text",
                files={"audio": (filename, audio_data, "audio/webm")},
                headers=get_auth_headers(),
                timeout=30.0
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

            print("\nDefault language (en) works correctly")


class TestTextToSpeech:
    """Test suite for Text-to-Speech endpoint."""

    @patch('app.services.voice_service.VoiceService.text_to_speech')
    def test_01_text_to_speech_success(self, mock_tts):
        """Test POST /api/v1/text-to-speech - Successful TTS."""
        # Create dummy MP3 audio data
        dummy_audio = b'\xff\xfb\x90\x00' + b'\x00' * 1000

        mock_tts.return_value = {
            "success": True,
            "audio_data": dummy_audio,
            "format": "mp3",
            "error": None
        }

        request_data = {
            "text": "Hello, this is a test",
            "voice": "alloy",
            "speed": 1.0
        }

        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/text-to-speech",
                json=request_data,
                headers=get_auth_headers(),
                timeout=30.0
            )

            assert response.status_code == 200, f"Failed TTS: {response.text}"
            data = response.json()

            assert data["success"] is True
            assert data["audio_base64"] is not None
            assert data["format"] == "mp3"
            assert data["error"] is None

            # Verify audio data is base64 encoded
            decoded_audio = base64.b64decode(data["audio_base64"])
            assert len(decoded_audio) > 0

            mock_tts.assert_called_once()

            print(f"\nSuccessfully generated speech audio ({len(decoded_audio)} bytes)")

    @patch('app.services.voice_service.VoiceService.text_to_speech')
    def test_02_text_to_speech_different_voices(self, mock_tts):
        """Test TTS with different voice options."""
        voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

        for voice in voices:
            dummy_audio = b'\xff\xfb\x90\x00' + b'\x00' * 500

            mock_tts.return_value = {
                "success": True,
                "audio_data": dummy_audio,
                "format": "mp3",
                "error": None
            }

            request_data = {
                "text": f"Testing {voice} voice",
                "voice": voice,
                "speed": 1.0
            }

            with httpx.Client() as client:
                response = client.post(
                    f"{API_V1}/text-to-speech",
                    json=request_data,
                    headers=get_auth_headers(),
                    timeout=30.0
                )

                assert response.status_code == 200, f"Failed for voice {voice}"
                data = response.json()
                assert data["success"] is True

            print(f"Tested voice: {voice}")

    @patch('app.services.voice_service.VoiceService.text_to_speech')
    def test_03_text_to_speech_different_speeds(self, mock_tts):
        """Test TTS with different speed settings."""
        speeds = [0.25, 0.5, 1.0, 1.5, 2.0, 4.0]

        for speed in speeds:
            dummy_audio = b'\xff\xfb\x90\x00' + b'\x00' * 500

            mock_tts.return_value = {
                "success": True,
                "audio_data": dummy_audio,
                "format": "mp3",
                "error": None
            }

            request_data = {
                "text": "Speed test",
                "voice": "alloy",
                "speed": speed
            }

            with httpx.Client() as client:
                response = client.post(
                    f"{API_V1}/text-to-speech",
                    json=request_data,
                    headers=get_auth_headers(),
                    timeout=30.0
                )

                assert response.status_code == 200, f"Failed for speed {speed}"
                data = response.json()
                assert data["success"] is True

            print(f"Tested speed: {speed}x")

    def test_04_text_to_speech_empty_text(self):
        """Test TTS with empty text."""
        request_data = {
            "text": "",
            "voice": "alloy",
            "speed": 1.0
        }

        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/text-to-speech",
                json=request_data,
                headers=get_auth_headers(),
                timeout=30.0
            )

            assert response.status_code == 400, "Should reject empty text"
            data = response.json()
            assert "empty" in data["detail"].lower() or "cannot be empty" in data["detail"].lower()

            print("\nCorrectly rejected empty text")

    def test_05_text_to_speech_whitespace_only(self):
        """Test TTS with whitespace-only text."""
        request_data = {
            "text": "   \n\t   ",
            "voice": "alloy",
            "speed": 1.0
        }

        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/text-to-speech",
                json=request_data,
                headers=get_auth_headers(),
                timeout=30.0
            )

            assert response.status_code == 400, "Should reject whitespace-only text"
            print("\nCorrectly rejected whitespace-only text")

    def test_06_text_to_speech_missing_text(self):
        """Test TTS without text field."""
        request_data = {
            "voice": "alloy",
            "speed": 1.0
        }

        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/text-to-speech",
                json=request_data,
                headers=get_auth_headers(),
                timeout=30.0
            )

            assert response.status_code == 422, "Should require text field"
            print("\nCorrectly rejected request without text")

    @patch('app.services.voice_service.VoiceService.text_to_speech')
    def test_07_text_to_speech_long_text(self, mock_tts):
        """Test TTS with long text."""
        long_text = "This is a test. " * 100  # ~1600 characters

        dummy_audio = b'\xff\xfb\x90\x00' + b'\x00' * 5000

        mock_tts.return_value = {
            "success": True,
            "audio_data": dummy_audio,
            "format": "mp3",
            "error": None
        }

        request_data = {
            "text": long_text,
            "voice": "alloy",
            "speed": 1.0
        }

        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/text-to-speech",
                json=request_data,
                headers=get_auth_headers(),
                timeout=30.0
            )

            assert response.status_code == 200, "Should handle long text"
            data = response.json()
            assert data["success"] is True

            print(f"\nSuccessfully handled long text ({len(long_text)} chars)")

    @patch('app.services.voice_service.VoiceService.text_to_speech')
    def test_08_text_to_speech_special_characters(self, mock_tts):
        """Test TTS with special characters and unicode."""
        special_texts = [
            "Hello! How are you? I'm fine, thanks.",
            "Numbers: 1, 2, 3... 100!",
            "Email: test@example.com, URL: https://example.com",
            "Unicode: 你好世界 Привет мир مرحبا بالعالم"
        ]

        for text in special_texts:
            dummy_audio = b'\xff\xfb\x90\x00' + b'\x00' * 500

            mock_tts.return_value = {
                "success": True,
                "audio_data": dummy_audio,
                "format": "mp3",
                "error": None
            }

            request_data = {
                "text": text,
                "voice": "alloy",
                "speed": 1.0
            }

            with httpx.Client() as client:
                response = client.post(
                    f"{API_V1}/text-to-speech",
                    json=request_data,
                    headers=get_auth_headers(),
                    timeout=30.0
                )

                assert response.status_code == 200, f"Failed for text: {text[:50]}"
                data = response.json()
                assert data["success"] is True

            print(f"Tested: {text[:50]}...")

    @patch('app.services.voice_service.VoiceService.text_to_speech')
    def test_09_text_to_speech_default_parameters(self, mock_tts):
        """Test TTS with default voice and speed."""
        dummy_audio = b'\xff\xfb\x90\x00' + b'\x00' * 500

        mock_tts.return_value = {
            "success": True,
            "audio_data": dummy_audio,
            "format": "mp3",
            "error": None
        }

        request_data = {
            "text": "Testing defaults"
        }

        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/text-to-speech",
                json=request_data,
                headers=get_auth_headers(),
                timeout=30.0
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

            print("\nDefault parameters work correctly")

    @patch('app.services.voice_service.VoiceService.text_to_speech')
    def test_10_text_to_speech_service_failure(self, mock_tts):
        """Test handling of TTS service failure."""
        mock_tts.return_value = {
            "success": False,
            "audio_data": b"",
            "format": "mp3",
            "error": "OpenAI API key not configured"
        }

        request_data = {
            "text": "Test failure",
            "voice": "alloy",
            "speed": 1.0
        }

        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/text-to-speech",
                json=request_data,
                headers=get_auth_headers(),
                timeout=30.0
            )

            assert response.status_code == 500, "Should return 500 on service failure"
            print("\nCorrectly handled TTS service failure")

    def test_11_text_to_speech_requires_auth(self):
        """Test that TTS requires authentication."""
        request_data = {
            "text": "Test authentication",
            "voice": "alloy",
            "speed": 1.0
        }

        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/text-to-speech",
                json=request_data,
                timeout=30.0
            )

            assert response.status_code in [401, 403], "Should require authentication"
            print("\nText-to-speech correctly requires authentication")


class TestTextToSpeechAudio:
    """Test suite for Text-to-Speech audio endpoint (direct audio response)."""

    @patch('app.services.voice_service.VoiceService.text_to_speech')
    def test_01_text_to_speech_audio_success(self, mock_tts):
        """Test POST /api/v1/text-to-speech/audio - Direct audio response."""
        dummy_audio = b'\xff\xfb\x90\x00' + b'\x00' * 1000

        mock_tts.return_value = {
            "success": True,
            "audio_data": dummy_audio,
            "format": "mp3",
            "error": None
        }

        request_data = {
            "text": "Direct audio test",
            "voice": "alloy",
            "speed": 1.0
        }

        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/text-to-speech/audio",
                json=request_data,
                headers=get_auth_headers(),
                timeout=30.0
            )

            assert response.status_code == 200, f"Failed: {response.text}"

            # Check content type
            assert response.headers["content-type"] == "audio/mpeg"

            # Check audio data
            assert len(response.content) > 0
            assert response.content == dummy_audio

            print(f"\nDirect audio response works ({len(response.content)} bytes)")

    @patch('app.services.voice_service.VoiceService.text_to_speech')
    def test_02_text_to_speech_audio_content_disposition(self, mock_tts):
        """Test that audio response has correct content-disposition header."""
        dummy_audio = b'\xff\xfb\x90\x00' + b'\x00' * 500

        mock_tts.return_value = {
            "success": True,
            "audio_data": dummy_audio,
            "format": "mp3",
            "error": None
        }

        request_data = {
            "text": "Header test",
            "voice": "alloy",
            "speed": 1.0
        }

        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/text-to-speech/audio",
                json=request_data,
                headers=get_auth_headers(),
                timeout=30.0
            )

            assert response.status_code == 200
            assert "content-disposition" in response.headers
            assert "speech.mp3" in response.headers["content-disposition"]

            print("\nContent-disposition header is correct")

    def test_03_text_to_speech_audio_empty_text(self):
        """Test audio endpoint with empty text."""
        request_data = {
            "text": "",
            "voice": "alloy",
            "speed": 1.0
        }

        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/text-to-speech/audio",
                json=request_data,
                headers=get_auth_headers(),
                timeout=30.0
            )

            assert response.status_code == 400, "Should reject empty text"
            print("\nAudio endpoint correctly rejects empty text")


class TestTextToSpeechStream:
    """Test suite for Text-to-Speech streaming endpoint."""

    @patch('app.services.voice_service.VoiceService.text_to_speech_stream')
    def test_01_text_to_speech_stream_success(self, mock_tts_stream):
        """Test POST /api/v1/text-to-speech/stream - Streaming response."""
        # Mock streaming response
        dummy_audio_chunks = [
            b'\xff\xfb\x90\x00' + b'\x00' * 500,
            b'\x00' * 500
        ]

        mock_tts_stream.return_value = iter(dummy_audio_chunks)

        request_data = {
            "text": "Streaming test",
            "voice": "alloy",
            "speed": 1.0
        }

        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/text-to-speech/stream",
                json=request_data,
                headers=get_auth_headers(),
                timeout=30.0
            )

            assert response.status_code == 200, f"Failed: {response.text}"

            # Check content type
            assert response.headers["content-type"] == "audio/mpeg"

            # Check that we got audio data
            assert len(response.content) > 0

            print(f"\nStreaming response works ({len(response.content)} bytes)")

    def test_02_text_to_speech_stream_empty_text(self):
        """Test streaming endpoint with empty text."""
        request_data = {
            "text": "",
            "voice": "alloy",
            "speed": 1.0
        }

        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/text-to-speech/stream",
                json=request_data,
                headers=get_auth_headers(),
                timeout=30.0
            )

            assert response.status_code == 400, "Should reject empty text"
            print("\nStreaming endpoint correctly rejects empty text")

    def test_03_text_to_speech_stream_requires_auth(self):
        """Test that streaming requires authentication."""
        request_data = {
            "text": "Auth test",
            "voice": "alloy",
            "speed": 1.0
        }

        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/text-to-speech/stream",
                json=request_data,
                timeout=30.0
            )

            assert response.status_code in [401, 403], "Should require authentication"
            print("\nStreaming endpoint correctly requires authentication")


class TestVoiceAPIEdgeCases:
    """Test edge cases and error scenarios."""

    @patch('app.services.voice_service.VoiceService.speech_to_text')
    def test_01_large_audio_file(self, mock_stt):
        """Test handling of large audio file."""
        mock_stt.return_value = {
            "success": True,
            "text": "Large file transcription",
            "language": "en",
            "error": None
        }

        # Create large audio file (10MB)
        filename, audio_data = create_test_audio_file("mp3", size=10 * 1024 * 1024)

        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/speech-to-text",
                files={"audio": (filename, audio_data, "audio/mp3")},
                data={"language": "en"},
                headers=get_auth_headers(),
                timeout=60.0
            )

            # Should handle large files (or return appropriate error)
            assert response.status_code in [200, 413], "Should handle or reject large files"

            if response.status_code == 200:
                print("\nSuccessfully handled large audio file")
            else:
                print("\nCorrectly rejected too-large audio file")

    @patch('app.services.voice_service.VoiceService.text_to_speech')
    def test_02_very_long_text_tts(self, mock_tts):
        """Test TTS with very long text (near limits)."""
        # OpenAI TTS has a 4096 character limit
        very_long_text = "This is a very long text. " * 150  # ~3900 characters

        dummy_audio = b'\xff\xfb\x90\x00' + b'\x00' * 5000

        mock_tts.return_value = {
            "success": True,
            "audio_data": dummy_audio,
            "format": "mp3",
            "error": None
        }

        request_data = {
            "text": very_long_text,
            "voice": "alloy",
            "speed": 1.0
        }

        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/text-to-speech",
                json=request_data,
                headers=get_auth_headers(),
                timeout=60.0
            )

            # Should either succeed or fail gracefully
            assert response.status_code in [200, 400, 500]
            print(f"\nHandled very long text ({len(very_long_text)} chars)")

    @patch('app.services.voice_service.VoiceService.speech_to_text')
    def test_03_concurrent_requests(self, mock_stt):
        """Test handling of concurrent voice requests."""
        import concurrent.futures

        mock_stt.return_value = {
            "success": True,
            "text": "Concurrent test",
            "language": "en",
            "error": None
        }

        def make_request(i):
            filename, audio_data = create_test_audio_file("webm")
            with httpx.Client() as client:
                response = client.post(
                    f"{API_V1}/speech-to-text",
                    files={"audio": (filename, audio_data, "audio/webm")},
                    data={"language": "en"},
                    headers=get_auth_headers(),
                    timeout=30.0
                )
                return response.status_code

        # Make 5 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request, i) for i in range(5)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        # All should succeed
        assert all(status == 200 for status in results), "All concurrent requests should succeed"
        print(f"\nSuccessfully handled {len(results)} concurrent requests")

    def test_04_invalid_content_type(self):
        """Test with invalid content type."""
        filename, audio_data = create_test_audio_file("txt")  # Text file, not audio

        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/speech-to-text",
                files={"audio": (filename, audio_data, "text/plain")},
                data={"language": "en"},
                headers=get_auth_headers(),
                timeout=30.0
            )

            # Endpoint should still accept it (format determined by extension)
            # But service might fail
            print(f"\nHandled invalid content type: {response.status_code}")

    @patch('app.services.voice_service.VoiceService.text_to_speech')
    def test_05_edge_case_speed_values(self, mock_tts):
        """Test TTS with edge case speed values."""
        edge_speeds = [0.25, 4.0]  # Min and max

        for speed in edge_speeds:
            dummy_audio = b'\xff\xfb\x90\x00' + b'\x00' * 500

            mock_tts.return_value = {
                "success": True,
                "audio_data": dummy_audio,
                "format": "mp3",
                "error": None
            }

            request_data = {
                "text": "Edge speed test",
                "voice": "alloy",
                "speed": speed
            }

            with httpx.Client() as client:
                response = client.post(
                    f"{API_V1}/text-to-speech",
                    json=request_data,
                    headers=get_auth_headers(),
                    timeout=30.0
                )

                assert response.status_code == 200, f"Failed for speed {speed}"
                print(f"Tested edge speed: {speed}x")


class TestVoiceAPIConfiguration:
    """Test API behavior with/without OpenAI configuration."""

    def test_01_endpoints_available_without_api_key(self):
        """Test that endpoints are available even without API key (will fail gracefully)."""
        # This test verifies the API structure is correct
        # Actual failures are handled in service layer

        request_data = {
            "text": "Test without key",
            "voice": "alloy",
            "speed": 1.0
        }

        with httpx.Client() as client:
            # TTS endpoint should be reachable
            response = client.post(
                f"{API_V1}/text-to-speech",
                json=request_data,
                headers=get_auth_headers(),
                timeout=30.0
            )

            # Should return error or success depending on config
            assert response.status_code in [200, 500]
            print(f"\nTTS endpoint reachable (status: {response.status_code})")

            # STT endpoint should be reachable
            filename, audio_data = create_test_audio_file("webm")
            response = client.post(
                f"{API_V1}/speech-to-text",
                files={"audio": (filename, audio_data, "audio/webm")},
                data={"language": "en"},
                headers=get_auth_headers(),
                timeout=30.0
            )

            # Should return error or success depending on config
            assert response.status_code in [200, 500]
            print(f"STT endpoint reachable (status: {response.status_code})")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
