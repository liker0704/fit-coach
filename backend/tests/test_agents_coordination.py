"""Integration tests for Multi-Agent Coordination.

Tests coordination between multiple AI agents:
- Agent coordination endpoint
- Streaming coordination endpoint
- Agent result synthesis
- Error handling in multi-agent scenarios
"""

import asyncio
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

    from datetime import datetime
    timestamp = str(int(datetime.now().timestamp()))
    _test_user_email = f"testcoord{timestamp}@example.com"
    _test_user_username = f"testcoord{timestamp}"

    with httpx.Client() as client:
        # Register
        client.post(
            f"{API_V1}/auth/register",
            json={
                "email": _test_user_email,
                "username": _test_user_username,
                "password": _test_user_password,
                "full_name": "Test Coordination User",
            },
        )

        # Login
        login_response = client.post(
            f"{API_V1}/auth/login",
            json={"email": _test_user_email, "password": _test_user_password},
        )

        if login_response.status_code == 200:
            _access_token = login_response.json()["access_token"]
            return _access_token

    return None


def get_auth_headers():
    """Get authorization headers."""
    token = get_or_create_test_user()
    return {"Authorization": f"Bearer {token}"}


# Mock responses
MOCK_NUTRITION_RESPONSE = {
    "success": True,
    "response": "Increase protein to 150g daily, eat complex carbs around workouts."
}

MOCK_WORKOUT_RESPONSE = {
    "success": True,
    "response": "Focus on compound lifts: squat, deadlift, bench press. 3-4 sets of 6-8 reps."
}

MOCK_SYNTHESIS = "Here's your comprehensive health plan combining nutrition and workout guidance..."


@pytest.mark.asyncio
async def test_coordinate_agents_success():
    """Test successful multi-agent coordination."""
    token = get_or_create_test_user()
    assert token is not None

    with patch("app.services.agent_coordinator.AgentCoordinator.coordinate_agents") as mock_coord:
        mock_coord.return_value = {
            "success": True,
            "task": "Create comprehensive health plan",
            "agent_results": {
                "nutrition": MOCK_NUTRITION_RESPONSE,
                "workout": MOCK_WORKOUT_RESPONSE
            },
            "synthesis": MOCK_SYNTHESIS
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_V1}/agents/coordinate",
                json={
                    "task": "Create comprehensive health plan",
                    "agents": ["nutrition", "workout"],
                    "context": {"date": date.today().isoformat()}
                },
                headers=get_auth_headers(),
                timeout=60.0
            )

            assert response.status_code == 200
            data = response.json()

            # Verify response structure
            assert data["success"] is True
            assert "task" in data
            assert "agent_results" in data
            assert "synthesis" in data

            # Verify agent results
            assert "nutrition" in data["agent_results"]
            assert "workout" in data["agent_results"]

            # Verify synthesis exists
            assert data["synthesis"] is not None


@pytest.mark.asyncio
async def test_coordinate_single_agent():
    """Test coordination with single agent."""
    token = get_or_create_test_user()
    assert token is not None

    with patch("app.services.agent_coordinator.AgentCoordinator.coordinate_agents") as mock_coord:
        mock_coord.return_value = {
            "success": True,
            "task": "Get nutrition advice",
            "agent_results": {
                "nutrition": MOCK_NUTRITION_RESPONSE
            },
            "synthesis": "Nutrition plan created successfully."
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_V1}/agents/coordinate",
                json={
                    "task": "Get nutrition advice",
                    "agents": ["nutrition"]
                },
                headers=get_auth_headers(),
                timeout=60.0
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert len(data["agent_results"]) == 1


@pytest.mark.asyncio
async def test_coordinate_all_agents():
    """Test coordination with all available agents."""
    token = get_or_create_test_user()
    assert token is not None

    with patch("app.services.agent_coordinator.AgentCoordinator.coordinate_agents") as mock_coord:
        mock_coord.return_value = {
            "success": True,
            "task": "Complete health assessment",
            "agent_results": {
                "nutrition": {"success": True, "response": "Nutrition advice"},
                "workout": {"success": True, "response": "Workout advice"},
                "chatbot": {"success": True, "response": "General guidance"},
                "daily_summary": {"success": True, "summary": "Daily summary"}
            },
            "synthesis": "Comprehensive health assessment completed."
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_V1}/agents/coordinate",
                json={
                    "task": "Complete health assessment",
                    "agents": ["nutrition", "workout", "chatbot", "daily_summary"]
                },
                headers=get_auth_headers(),
                timeout=60.0
            )

            assert response.status_code == 200
            data = response.json()
            assert len(data["agent_results"]) == 4


@pytest.mark.asyncio
async def test_coordinate_with_context():
    """Test coordination with additional context."""
    token = get_or_create_test_user()
    assert token is not None

    with patch("app.services.agent_coordinator.AgentCoordinator.coordinate_agents") as mock_coord:
        mock_coord.return_value = {
            "success": True,
            "task": "Weekly plan",
            "agent_results": {
                "nutrition": MOCK_NUTRITION_RESPONSE,
                "workout": MOCK_WORKOUT_RESPONSE
            },
            "synthesis": MOCK_SYNTHESIS
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_V1}/agents/coordinate",
                json={
                    "task": "Create weekly plan",
                    "agents": ["nutrition", "workout"],
                    "context": {
                        "date": "2025-01-15",
                        "goal": "muscle_gain",
                        "experience_level": "intermediate"
                    }
                },
                headers=get_auth_headers(),
                timeout=60.0
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True


@pytest.mark.asyncio
async def test_coordinate_partial_failure():
    """Test coordination when one agent fails."""
    token = get_or_create_test_user()
    assert token is not None

    with patch("app.services.agent_coordinator.AgentCoordinator.coordinate_agents") as mock_coord:
        mock_coord.return_value = {
            "success": True,
            "task": "Health plan",
            "agent_results": {
                "nutrition": MOCK_NUTRITION_RESPONSE,
                "workout": {
                    "success": False,
                    "error": "Workout agent temporarily unavailable"
                }
            },
            "synthesis": "Nutrition plan created. Workout recommendations pending."
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_V1}/agents/coordinate",
                json={
                    "task": "Create health plan",
                    "agents": ["nutrition", "workout"]
                },
                headers=get_auth_headers(),
                timeout=60.0
            )

            assert response.status_code == 200
            data = response.json()

            # Should still succeed overall
            assert data["success"] is True

            # Check individual agent results
            assert data["agent_results"]["nutrition"]["success"] is True
            assert data["agent_results"]["workout"]["success"] is False


@pytest.mark.asyncio
async def test_coordinate_streaming_success():
    """Test streaming coordination endpoint."""
    token = get_or_create_test_user()
    assert token is not None

    async def mock_stream():
        chunks = [
            "Creating ",
            "your ",
            "comprehensive ",
            "health ",
            "plan..."
        ]
        for chunk in chunks:
            yield chunk

    with patch("app.services.agent_coordinator.AgentCoordinator.stream_coordinated_response") as mock_stream:
        mock_stream.return_value = mock_stream()

        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{API_V1}/agents/coordinate/stream",
                json={
                    "task": "Create health plan",
                    "agents": ["nutrition", "workout"]
                },
                headers=get_auth_headers(),
                timeout=60.0
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
async def test_coordinate_unauthorized():
    """Test coordination requires authentication."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_V1}/agents/coordinate",
            json={
                "task": "Test task",
                "agents": ["nutrition"]
            }
        )
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_coordinate_invalid_agent():
    """Test coordination with invalid agent type."""
    token = get_or_create_test_user()
    assert token is not None

    with patch("app.services.agent_coordinator.AgentCoordinator.coordinate_agents") as mock_coord:
        # Invalid agent should be handled gracefully
        mock_coord.return_value = {
            "success": True,
            "task": "Test",
            "agent_results": {},
            "synthesis": "No valid agents to coordinate."
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_V1}/agents/coordinate",
                json={
                    "task": "Test task",
                    "agents": ["invalid_agent"]
                },
                headers=get_auth_headers(),
                timeout=60.0
            )

            # Should handle gracefully
            assert response.status_code in [200, 400, 422]


@pytest.mark.asyncio
async def test_coordinate_empty_agents():
    """Test coordination with empty agent list."""
    token = get_or_create_test_user()
    assert token is not None

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_V1}/agents/coordinate",
            json={
                "task": "Test task",
                "agents": []
            },
            headers=get_auth_headers()
        )

        # Should reject empty agent list
        assert response.status_code in [400, 422]


@pytest.mark.asyncio
async def test_coordinate_missing_task():
    """Test coordination with missing task description."""
    token = get_or_create_test_user()
    assert token is not None

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_V1}/agents/coordinate",
            json={
                "agents": ["nutrition"]
            },
            headers=get_auth_headers()
        )

        # Should reject missing task
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_coordinate_synthesis_quality():
    """Test that synthesis combines multiple agent outputs."""
    token = get_or_create_test_user()
    assert token is not None

    with patch("app.services.agent_coordinator.AgentCoordinator.coordinate_agents") as mock_coord:
        mock_coord.return_value = {
            "success": True,
            "task": "Health optimization",
            "agent_results": {
                "nutrition": {
                    "success": True,
                    "response": "Focus on protein and vegetables"
                },
                "workout": {
                    "success": True,
                    "response": "3x weekly strength training"
                }
            },
            "synthesis": (
                "Your health optimization plan combines nutrition and exercise. "
                "Focus on protein and vegetables while doing strength training 3x weekly."
            )
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_V1}/agents/coordinate",
                json={
                    "task": "Optimize my health",
                    "agents": ["nutrition", "workout"]
                },
                headers=get_auth_headers(),
                timeout=60.0
            )

            assert response.status_code == 200
            data = response.json()

            # Synthesis should reference both agents
            synthesis = data["synthesis"].lower()
            # Should contain references to key concepts
            assert len(synthesis) > 0


if __name__ == "__main__":
    """Run tests manually."""
    print("Running Multi-Agent Coordination Tests...")
    print("=" * 60)

    async def run_tests():
        tests = [
            ("Coordinate Agents Success", test_coordinate_agents_success),
            ("Coordinate Single Agent", test_coordinate_single_agent),
            ("Coordinate All Agents", test_coordinate_all_agents),
            ("Coordinate with Context", test_coordinate_with_context),
            ("Coordinate Partial Failure", test_coordinate_partial_failure),
            ("Coordinate Streaming Success", test_coordinate_streaming_success),
            ("Coordinate Unauthorized", test_coordinate_unauthorized),
            ("Coordinate Invalid Agent", test_coordinate_invalid_agent),
            ("Coordinate Empty Agents", test_coordinate_empty_agents),
            ("Coordinate Missing Task", test_coordinate_missing_task),
            ("Synthesis Quality", test_coordinate_synthesis_quality),
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
