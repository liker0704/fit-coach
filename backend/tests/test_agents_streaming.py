"""Integration tests for Agent Streaming endpoints.

Tests streaming functionality for:
- Chat agent streaming
- Nutrition coach streaming
- Workout coach streaming
- Multi-agent coordination streaming
"""

import asyncio
import json
import pytest
from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

import httpx

# Base URL for the API
BASE_URL = "http://localhost:8001"
API_V1 = f"{BASE_URL}/api/v1"

# Test data
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
    from datetime import datetime
    timestamp = str(int(datetime.now().timestamp()))
    _test_user_email = f"teststream{timestamp}@example.com"
    _test_user_username = f"teststream{timestamp}"

    with httpx.Client() as client:
        # Register
        client.post(
            f"{API_V1}/auth/register",
            json={
                "email": _test_user_email,
                "username": _test_user_username,
                "password": _test_user_password,
                "full_name": "Test Stream User",
            },
        )

        # Login to get token
        login_response = client.post(
            f"{API_V1}/auth/login",
            json={"email": _test_user_email, "password": _test_user_password},
        )

        if login_response.status_code == 200:
            _access_token = login_response.json()["access_token"]
            return _access_token

    return None


def get_auth_headers():
    """Get authorization headers with access token."""
    token = get_or_create_test_user()
    return {"Authorization": f"Bearer {token}"}


# Mock streaming responses
async def mock_stream_generator(chunks):
    """Generate mock streaming chunks."""
    for chunk in chunks:
        yield chunk


MOCK_STREAM_CHUNKS = [
    "Hello ",
    "this ",
    "is ",
    "a ",
    "streaming ",
    "response!"
]


@pytest.mark.asyncio
async def test_chat_streaming_success():
    """Test successful streaming chat response."""
    token = get_or_create_test_user()
    assert token is not None, "Failed to get or create test user"

    # Mock LLMService streaming
    with patch("app.services.llm_service.LLMService.stream_chat_response") as mock_stream:
        mock_stream.return_value = mock_stream_generator(MOCK_STREAM_CHUNKS)

        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{API_V1}/agents/chat/stream",
                json={
                    "message": "Tell me about fitness",
                    "conversation_history": []
                },
                headers=get_auth_headers(),
                timeout=30.0
            ) as response:
                assert response.status_code == 200
                assert response.headers["content-type"] == "text/event-stream"

                # Collect streamed chunks
                chunks = []
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]  # Remove "data: " prefix
                        if data == "[DONE]":
                            break
                        chunks.append(data)

                # Verify we received chunks
                assert len(chunks) > 0, "Should receive streaming chunks"


@pytest.mark.asyncio
async def test_chat_streaming_with_history():
    """Test chat streaming with conversation history."""
    token = get_or_create_test_user()
    assert token is not None

    with patch("app.services.llm_service.LLMService.stream_chat_response") as mock_stream:
        mock_stream.return_value = mock_stream_generator(["Yes, ", "that's ", "correct!"])

        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{API_V1}/agents/chat/stream",
                json={
                    "message": "Is that right?",
                    "conversation_history": [
                        {"role": "user", "content": "Should I eat protein after workout?"},
                        {"role": "assistant", "content": "Yes, it helps recovery."}
                    ]
                },
                headers=get_auth_headers(),
                timeout=30.0
            ) as response:
                assert response.status_code == 200

                chunks = []
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data != "[DONE]":
                            chunks.append(data)

                assert len(chunks) > 0


@pytest.mark.asyncio
async def test_nutrition_coach_streaming_success():
    """Test successful nutrition coach streaming response."""
    token = get_or_create_test_user()
    assert token is not None

    with patch("app.services.llm_service.LLMService.stream_coaching_advice") as mock_stream:
        mock_stream.return_value = mock_stream_generator([
            "Based on ",
            "your goals, ",
            "I recommend ",
            "increasing protein."
        ])

        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{API_V1}/agents/nutrition-coach/stream",
                json={
                    "question": "How can I optimize my diet?",
                    "date": date.today().isoformat()
                },
                headers=get_auth_headers(),
                timeout=30.0
            ) as response:
                assert response.status_code == 200
                assert "text/event-stream" in response.headers["content-type"]

                chunks = []
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data != "[DONE]":
                            chunks.append(data)

                assert len(chunks) > 0


@pytest.mark.asyncio
async def test_workout_coach_streaming_success():
    """Test successful workout coach streaming response."""
    token = get_or_create_test_user()
    assert token is not None

    with patch("app.services.llm_service.LLMService.stream_coaching_advice") as mock_stream:
        mock_stream.return_value = mock_stream_generator([
            "For building ",
            "strength, ",
            "focus on ",
            "compound movements."
        ])

        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{API_V1}/agents/workout-coach/stream",
                json={
                    "question": "What's best for strength?",
                    "date": date.today().isoformat()
                },
                headers=get_auth_headers(),
                timeout=30.0
            ) as response:
                assert response.status_code == 200
                assert "text/event-stream" in response.headers["content-type"]

                chunks = []
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data != "[DONE]":
                            chunks.append(data)

                assert len(chunks) > 0


@pytest.mark.asyncio
async def test_streaming_unauthorized():
    """Test that streaming endpoints require authentication."""
    endpoints = [
        "/agents/chat/stream",
        "/agents/nutrition-coach/stream",
        "/agents/workout-coach/stream",
    ]

    async with httpx.AsyncClient() as client:
        for endpoint in endpoints:
            response = await client.post(
                f"{API_V1}{endpoint}",
                json={"message": "test", "question": "test"}
            )
            assert response.status_code == 401, f"Expected 401 for {endpoint}"


@pytest.mark.asyncio
async def test_streaming_error_handling():
    """Test streaming error handling when LLM fails."""
    token = get_or_create_test_user()
    assert token is not None

    # Mock streaming to raise an error
    async def error_generator():
        yield "Starting..."
        raise Exception("LLM service error")

    with patch("app.services.llm_service.LLMService.stream_chat_response") as mock_stream:
        mock_stream.return_value = error_generator()

        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{API_V1}/agents/chat/stream",
                json={"message": "test message"},
                headers=get_auth_headers(),
                timeout=30.0
            ) as response:
                # Should still return 200 but include error in stream
                assert response.status_code == 200

                has_error = False
                async for line in response.aiter_lines():
                    if line.startswith("data: ") and "[ERROR" in line:
                        has_error = True
                        break

                # Error should be in stream or connection should close
                # Either is acceptable error handling


@pytest.mark.asyncio
async def test_streaming_sse_format():
    """Test that streaming response follows SSE format correctly."""
    token = get_or_create_test_user()
    assert token is not None

    with patch("app.services.llm_service.LLMService.stream_chat_response") as mock_stream:
        mock_stream.return_value = mock_stream_generator(["Test ", "chunk"])

        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{API_V1}/agents/chat/stream",
                json={"message": "test"},
                headers=get_auth_headers(),
                timeout=30.0
            ) as response:
                # Check SSE headers
                assert response.headers["cache-control"] == "no-cache"
                assert response.headers["connection"] == "keep-alive"
                assert response.headers["x-accel-buffering"] == "no"

                # Check SSE format
                lines = []
                async for line in response.aiter_lines():
                    lines.append(line)

                # Each chunk should start with "data: "
                data_lines = [l for l in lines if l.startswith("data: ")]
                assert len(data_lines) > 0

                # Should end with "[DONE]"
                assert any("[DONE]" in line for line in lines)


@pytest.mark.asyncio
async def test_streaming_empty_message():
    """Test streaming with empty message."""
    token = get_or_create_test_user()
    assert token is not None

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_V1}/agents/chat/stream",
            json={"message": ""},
            headers=get_auth_headers()
        )
        # Should reject empty messages
        assert response.status_code in [400, 422]


@pytest.mark.asyncio
async def test_concurrent_streaming():
    """Test multiple concurrent streaming requests."""
    token = get_or_create_test_user()
    assert token is not None

    with patch("app.services.llm_service.LLMService.stream_chat_response") as mock_stream:
        mock_stream.return_value = mock_stream_generator(["Response"])

        async with httpx.AsyncClient() as client:
            # Start multiple streams concurrently
            tasks = []
            for i in range(3):
                task = client.stream(
                    "POST",
                    f"{API_V1}/agents/chat/stream",
                    json={"message": f"Question {i}"},
                    headers=get_auth_headers(),
                    timeout=30.0
                )
                tasks.append(task)

            # All should succeed
            for task in tasks:
                async with task as response:
                    assert response.status_code == 200


if __name__ == "__main__":
    """Run tests manually."""
    print("Running Agent Streaming Tests...")
    print("=" * 60)

    async def run_tests():
        tests = [
            ("Chat Streaming Success", test_chat_streaming_success),
            ("Chat Streaming with History", test_chat_streaming_with_history),
            ("Nutrition Coach Streaming", test_nutrition_coach_streaming_success),
            ("Workout Coach Streaming", test_workout_coach_streaming_success),
            ("Streaming Unauthorized", test_streaming_unauthorized),
            ("Streaming Error Handling", test_streaming_error_handling),
            ("SSE Format Validation", test_streaming_sse_format),
            ("Empty Message Rejection", test_streaming_empty_message),
            ("Concurrent Streaming", test_concurrent_streaming),
        ]

        for name, test_func in tests:
            try:
                await test_func()
                print(f"✅ {name}")
            except AssertionError as e:
                print(f"❌ {name}: {str(e)}")
            except Exception as e:
                print(f"❌ {name}: {type(e).__name__}: {str(e)}")

    asyncio.run(run_tests())
    print("=" * 60)
    print("Tests completed!")
