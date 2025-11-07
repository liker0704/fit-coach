"""Integration tests for AI Agents endpoints."""

import httpx
import pytest
from datetime import date, datetime
from unittest.mock import patch, MagicMock

# Base URL for the API
BASE_URL = "http://localhost:8001"
API_V1 = f"{BASE_URL}/api/v1"

# Global test data
_test_user_email = None
_test_user_password = "TestPassword123!"
_test_user_username = None
_access_token = None
_test_day_id = None


def get_or_create_test_user():
    """Get or create test user and return access token."""
    global _test_user_email, _test_user_username, _access_token

    if _access_token:
        return _access_token

    # Create unique username/email for this test session
    timestamp = str(int(datetime.now().timestamp()))
    _test_user_email = f"testagent{timestamp}@example.com"
    _test_user_username = f"testagent{timestamp}"

    with httpx.Client() as client:
        # Register
        response = client.post(
            f"{API_V1}/auth/register",
            json={
                "email": _test_user_email,
                "username": _test_user_username,
                "password": _test_user_password,
                "full_name": "Test Agent User",
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


def create_test_day(day_date=None):
    """Create a test day and return its ID."""
    global _test_day_id

    if day_date is None:
        day_date = date.today()

    with httpx.Client() as client:
        response = client.post(
            f"{API_V1}/days",
            json={"date": day_date.isoformat()},
            headers=get_auth_headers(),
        )

        if response.status_code == 200 or response.status_code == 201:
            day_data = response.json()
            _test_day_id = day_data["id"]
            return _test_day_id

    return None


# Mock LLM responses for testing
MOCK_DAILY_SUMMARY = """You had a great day today! You stayed active with 2 workouts and maintained good nutrition."""

MOCK_CHAT_RESPONSE = """That's a great question! I recommend focusing on progressive overload and proper form."""

MOCK_NUTRITION_ADVICE = """Based on your goals, I suggest increasing protein intake to 150g per day and timing your carbs around workouts."""

MOCK_WORKOUT_ADVICE = """For building strength, focus on compound movements like squats, deadlifts, and bench press. Aim for 3-4 sets of 6-8 reps."""


@pytest.mark.asyncio
async def test_daily_summary_agent():
    """Test the Daily Summary Agent endpoint."""
    # Ensure test user exists
    token = get_or_create_test_user()
    assert token is not None, "Failed to get or create test user"

    # Create a test day
    day_id = create_test_day()
    assert day_id is not None, "Failed to create test day"

    # Mock the agent's execute method
    with patch(
        "app.agents.agents.daily_summary.DailySummaryAgent.execute"
    ) as mock_execute:
        mock_execute.return_value = {
            "summary": MOCK_DAILY_SUMMARY,
            "highlights": [
                "Completed 2 workouts",
                "Hit protein goal",
            ],
            "recommendations": [
                "Try to get 8 hours of sleep",
                "Drink more water tomorrow",
            ],
        }

        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/agents/daily-summary",
                json={"date": date.today().isoformat()},
                headers=get_auth_headers(),
            )

            assert response.status_code == 200, f"Unexpected status: {response.status_code}"
            data = response.json()

            # Verify response structure
            assert "summary" in data
            assert "highlights" in data
            assert "recommendations" in data
            assert "date" in data
            assert "generated_at" in data

            # Verify content
            assert data["summary"] == MOCK_DAILY_SUMMARY
            assert len(data["highlights"]) == 2
            assert len(data["recommendations"]) == 2


@pytest.mark.asyncio
async def test_chatbot_agent():
    """Test the Chatbot Agent endpoint."""
    token = get_or_create_test_user()
    assert token is not None, "Failed to get or create test user"

    with patch("app.agents.agents.chatbot.ChatbotAgent.execute") as mock_execute:
        mock_execute.return_value = {"response": MOCK_CHAT_RESPONSE}

        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/agents/chat",
                json={
                    "message": "What's the best way to build strength?",
                    "conversation_history": [],
                },
                headers=get_auth_headers(),
            )

            assert response.status_code == 200, f"Unexpected status: {response.status_code}"
            data = response.json()

            # Verify response structure
            assert "response" in data
            assert "generated_at" in data

            # Verify content
            assert data["response"] == MOCK_CHAT_RESPONSE


@pytest.mark.asyncio
async def test_chatbot_with_history():
    """Test the Chatbot Agent with conversation history."""
    token = get_or_create_test_user()
    assert token is not None, "Failed to get or create test user"

    with patch("app.agents.agents.chatbot.ChatbotAgent.execute") as mock_execute:
        mock_execute.return_value = {"response": "Yes, that's correct!"}

        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/agents/chat",
                json={
                    "message": "Is that right?",
                    "conversation_history": [
                        {"role": "user", "content": "Should I eat protein after workout?"},
                        {"role": "assistant", "content": "Yes, protein after workout helps with muscle recovery."},
                    ],
                },
                headers=get_auth_headers(),
            )

            assert response.status_code == 200
            data = response.json()
            assert "response" in data


@pytest.mark.asyncio
async def test_nutrition_coach_agent():
    """Test the Nutrition Coach Agent endpoint."""
    token = get_or_create_test_user()
    assert token is not None, "Failed to get or create test user"

    # Create a test day with some data
    day_id = create_test_day()
    assert day_id is not None

    with patch(
        "app.agents.agents.nutrition_coach.NutritionCoachAgent.execute"
    ) as mock_execute:
        mock_execute.return_value = {"response": MOCK_NUTRITION_ADVICE}

        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/agents/nutrition-coach",
                json={
                    "message": "How can I optimize my nutrition for muscle gain?",
                    "date": date.today().isoformat(),
                },
                headers=get_auth_headers(),
            )

            assert response.status_code == 200, f"Unexpected status: {response.status_code}"
            data = response.json()

            # Verify response structure
            assert "response" in data
            assert "generated_at" in data

            # Verify content
            assert data["response"] == MOCK_NUTRITION_ADVICE


@pytest.mark.asyncio
async def test_workout_coach_agent():
    """Test the Workout Coach Agent endpoint."""
    token = get_or_create_test_user()
    assert token is not None, "Failed to get or create test user"

    # Create a test day with some data
    day_id = create_test_day()
    assert day_id is not None

    with patch(
        "app.agents.agents.workout_coach.WorkoutCoachAgent.execute"
    ) as mock_execute:
        mock_execute.return_value = {"response": MOCK_WORKOUT_ADVICE}

        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/agents/workout-coach",
                json={
                    "message": "What's the best program for building strength?",
                    "date": date.today().isoformat(),
                },
                headers=get_auth_headers(),
            )

            assert response.status_code == 200, f"Unexpected status: {response.status_code}"
            data = response.json()

            # Verify response structure
            assert "response" in data
            assert "generated_at" in data

            # Verify content
            assert data["response"] == MOCK_WORKOUT_ADVICE


@pytest.mark.asyncio
async def test_agents_unauthorized():
    """Test that all agent endpoints require authentication."""
    endpoints = [
        ("/agents/daily-summary", {"date": date.today().isoformat()}),
        ("/agents/chat", {"message": "Hello"}),
        ("/agents/nutrition-coach", {"message": "Help with nutrition"}),
        ("/agents/workout-coach", {"message": "Help with workouts"}),
    ]

    with httpx.Client() as client:
        for endpoint, payload in endpoints:
            response = client.post(f"{API_V1}{endpoint}", json=payload)
            assert response.status_code == 401, f"Expected 401 for {endpoint}, got {response.status_code}"


@pytest.mark.asyncio
async def test_agents_invalid_payload():
    """Test agent endpoints with invalid payloads."""
    token = get_or_create_test_user()
    assert token is not None

    with httpx.Client() as client:
        # Daily summary with invalid date
        response = client.post(
            f"{API_V1}/agents/daily-summary",
            json={"date": "invalid-date"},
            headers=get_auth_headers(),
        )
        assert response.status_code in [400, 422], f"Expected validation error, got {response.status_code}"

        # Chat without message
        response = client.post(
            f"{API_V1}/agents/chat", json={}, headers=get_auth_headers()
        )
        assert response.status_code == 422, f"Expected 422, got {response.status_code}"

        # Nutrition coach without message
        response = client.post(
            f"{API_V1}/agents/nutrition-coach", json={}, headers=get_auth_headers()
        )
        assert response.status_code == 422, f"Expected 422, got {response.status_code}"

        # Workout coach without message
        response = client.post(
            f"{API_V1}/agents/workout-coach", json={}, headers=get_auth_headers()
        )
        assert response.status_code == 422, f"Expected 422, got {response.status_code}"


if __name__ == "__main__":
    """Run tests manually."""
    import asyncio

    print("Running Agents API Tests...")
    print("=" * 60)

    async def run_tests():
        tests = [
            ("Daily Summary Agent", test_daily_summary_agent),
            ("Chatbot Agent", test_chatbot_agent),
            ("Chatbot with History", test_chatbot_with_history),
            ("Nutrition Coach Agent", test_nutrition_coach_agent),
            ("Workout Coach Agent", test_workout_coach_agent),
            ("Unauthorized Access", test_agents_unauthorized),
            ("Invalid Payloads", test_agents_invalid_payload),
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
