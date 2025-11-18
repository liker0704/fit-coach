"""Integration tests for Goals API endpoints."""

import httpx
import pytest
from datetime import date, datetime, timedelta
from decimal import Decimal

# Base URL for the API
BASE_URL = "http://localhost:8001"
API_V1 = f"{BASE_URL}/api/v1"

# Global test data
_test_user_email = None
_test_user_password = "TestPassword123!"
_test_user_username = None
_access_token = None


def get_or_create_test_user():
    """Get or create test user and return credentials."""
    global _test_user_email, _test_user_username, _access_token

    if _access_token:
        return _access_token

    # Create unique username/email for this test session
    timestamp = str(int(datetime.now().timestamp()))
    _test_user_email = f"testgoals{timestamp}@example.com"
    _test_user_username = f"testgoals{timestamp}"

    with httpx.Client() as client:
        # Try to register
        response = client.post(
            f"{API_V1}/auth/register",
            json={
                "email": _test_user_email,
                "username": _test_user_username,
                "password": _test_user_password,
                "full_name": "Test User Goals"
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

        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        token_data = login_response.json()
        _access_token = token_data["access_token"]

        return _access_token


@pytest.fixture
def auth_headers():
    """Get authorization headers with access token."""
    token = get_or_create_test_user()
    return {"Authorization": f"Bearer {token}"}


# ===========================
# GOAL CRUD TESTS
# ===========================

class TestGoalCRUDAPI:
    """Test suite for Goal CRUD operations."""

    goal_id = None

    def test_01_create_goal(self, auth_headers):
        """Test POST /api/v1/goals - Create goal."""
        today = date.today()
        goal_data = {
            "type": "weight",
            "title": "Lose 10 kg",
            "description": "Weight loss goal for summer",
            "target_value": 70.0,
            "current_value": 80.0,
            "unit": "kg",
            "start_date": today.isoformat(),
            "end_date": (today + timedelta(days=90)).isoformat(),
            "status": "active"
        }

        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/goals",
                json=goal_data,
                headers=auth_headers,
                timeout=10.0
            )

            assert response.status_code == 201, f"Failed to create goal: {response.text}"
            data = response.json()

            # Verify response structure
            assert "id" in data, "Response missing 'id'"
            assert "user_id" in data, "Response missing 'user_id'"
            assert data["type"] == "weight"
            assert data["title"] == "Lose 10 kg"
            assert float(data["target_value"]) == 70.0
            assert float(data["current_value"]) == 80.0
            assert data["status"] == "active"

            # Save goal ID for later tests
            TestGoalCRUDAPI.goal_id = data["id"]

            print(f"\n✅ Created goal: ID={data['id']}, Title={data['title']}")

    def test_02_create_goal_validation_error(self, auth_headers):
        """Test POST /api/v1/goals - Validation error with end_date before start_date."""
        today = date.today()
        goal_data = {
            "type": "exercise",
            "title": "Invalid goal",
            "target_value": 100.0,
            "start_date": today.isoformat(),
            "end_date": (today - timedelta(days=1)).isoformat()  # Invalid: before start_date
        }

        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/goals",
                json=goal_data,
                headers=auth_headers,
                timeout=10.0
            )

            assert response.status_code == 422 or response.status_code == 400, \
                f"Should fail validation, got {response.status_code}"

            print(f"\n✅ Validation error handled correctly")

    def test_03_get_goals(self, auth_headers):
        """Test GET /api/v1/goals - Get all goals."""
        with httpx.Client() as client:
            response = client.get(
                f"{API_V1}/goals",
                headers=auth_headers,
                timeout=10.0
            )

            assert response.status_code == 200, f"Failed to get goals: {response.text}"
            data = response.json()

            assert isinstance(data, list), "Response should be a list"
            assert len(data) >= 1, "Should have at least one goal"

            # Verify our created goal is in the list
            goal_ids = [g["id"] for g in data]
            assert TestGoalCRUDAPI.goal_id in goal_ids, "Created goal should be in the list"

            print(f"\n✅ Retrieved {len(data)} goals")

    def test_04_get_goals_with_status_filter(self, auth_headers):
        """Test GET /api/v1/goals?status=active - Get goals filtered by status."""
        with httpx.Client() as client:
            response = client.get(
                f"{API_V1}/goals?status=active",
                headers=auth_headers,
                timeout=10.0
            )

            assert response.status_code == 200, f"Failed to get goals: {response.text}"
            data = response.json()

            assert isinstance(data, list), "Response should be a list"

            # All goals should have status 'active'
            for goal in data:
                assert goal["status"] == "active", f"Goal {goal['id']} should be active"

            print(f"\n✅ Retrieved {len(data)} active goals")

    def test_05_get_goals_invalid_status(self, auth_headers):
        """Test GET /api/v1/goals?status=invalid - Invalid status filter."""
        with httpx.Client() as client:
            response = client.get(
                f"{API_V1}/goals?status=invalid",
                headers=auth_headers,
                timeout=10.0
            )

            assert response.status_code == 400, f"Should return 400 for invalid status, got {response.status_code}"

            print(f"\n✅ Invalid status filter handled correctly")

    def test_06_get_goal_by_id(self, auth_headers):
        """Test GET /api/v1/goals/{goal_id} - Get specific goal."""
        assert TestGoalCRUDAPI.goal_id is not None, "No goal ID available"

        with httpx.Client() as client:
            response = client.get(
                f"{API_V1}/goals/{TestGoalCRUDAPI.goal_id}",
                headers=auth_headers,
                timeout=10.0
            )

            assert response.status_code == 200, f"Failed to get goal: {response.text}"
            data = response.json()

            assert data["id"] == TestGoalCRUDAPI.goal_id
            assert data["type"] == "weight"
            assert data["title"] == "Lose 10 kg"
            assert float(data["target_value"]) == 70.0

            print(f"\n✅ Retrieved goal: ID={data['id']}, Title={data['title']}")

    def test_07_get_goal_not_found(self, auth_headers):
        """Test GET /api/v1/goals/999999 - Goal not found."""
        with httpx.Client() as client:
            response = client.get(
                f"{API_V1}/goals/999999",
                headers=auth_headers,
                timeout=10.0
            )

            assert response.status_code == 404, f"Should return 404, got {response.status_code}"

            print(f"\n✅ Non-existent goal handled correctly")

    def test_08_update_goal(self, auth_headers):
        """Test PUT /api/v1/goals/{goal_id} - Update goal."""
        assert TestGoalCRUDAPI.goal_id is not None, "No goal ID available"

        update_data = {
            "current_value": 75.0,
            "title": "Updated: Lose 10 kg"
        }

        with httpx.Client() as client:
            response = client.put(
                f"{API_V1}/goals/{TestGoalCRUDAPI.goal_id}",
                json=update_data,
                headers=auth_headers,
                timeout=10.0
            )

            assert response.status_code == 200, f"Failed to update goal: {response.text}"
            data = response.json()

            assert float(data["current_value"]) == 75.0
            assert data["title"] == "Updated: Lose 10 kg"

            print(f"\n✅ Updated goal: ID={data['id']}, Current={data['current_value']}")

    def test_09_update_goal_status(self, auth_headers):
        """Test PUT /api/v1/goals/{goal_id} - Update goal status."""
        assert TestGoalCRUDAPI.goal_id is not None, "No goal ID available"

        update_data = {
            "status": "completed"
        }

        with httpx.Client() as client:
            response = client.put(
                f"{API_V1}/goals/{TestGoalCRUDAPI.goal_id}",
                json=update_data,
                headers=auth_headers,
                timeout=10.0
            )

            assert response.status_code == 200, f"Failed to update goal: {response.text}"
            data = response.json()

            assert data["status"] == "completed"
            assert "completed_at" in data

            print(f"\n✅ Updated goal status to completed")

    def test_10_update_goal_not_found(self, auth_headers):
        """Test PUT /api/v1/goals/999999 - Goal not found."""
        update_data = {
            "current_value": 65.0
        }

        with httpx.Client() as client:
            response = client.put(
                f"{API_V1}/goals/999999",
                json=update_data,
                headers=auth_headers,
                timeout=10.0
            )

            assert response.status_code == 404, f"Should return 404, got {response.status_code}"

            print(f"\n✅ Update non-existent goal handled correctly")

    def test_11_delete_goal(self, auth_headers):
        """Test DELETE /api/v1/goals/{goal_id} - Delete goal."""
        assert TestGoalCRUDAPI.goal_id is not None, "No goal ID available"

        with httpx.Client() as client:
            response = client.delete(
                f"{API_V1}/goals/{TestGoalCRUDAPI.goal_id}",
                headers=auth_headers,
                timeout=10.0
            )

            assert response.status_code == 204, f"Failed to delete goal: {response.text}"

            # Verify goal is deleted
            verify_response = client.get(
                f"{API_V1}/goals/{TestGoalCRUDAPI.goal_id}",
                headers=auth_headers,
                timeout=10.0
            )

            assert verify_response.status_code == 404, "Goal should be deleted"

            print(f"\n✅ Deleted goal: ID={TestGoalCRUDAPI.goal_id}")

    def test_12_delete_goal_not_found(self, auth_headers):
        """Test DELETE /api/v1/goals/999999 - Goal not found."""
        with httpx.Client() as client:
            response = client.delete(
                f"{API_V1}/goals/999999",
                headers=auth_headers,
                timeout=10.0
            )

            assert response.status_code == 404, f"Should return 404, got {response.status_code}"

            print(f"\n✅ Delete non-existent goal handled correctly")


# ===========================
# GOAL TYPE TESTS
# ===========================

class TestGoalTypes:
    """Test suite for different goal types."""

    def test_create_weight_goal(self, auth_headers):
        """Test creating a weight goal."""
        today = date.today()
        goal_data = {
            "type": "weight",
            "title": "Weight goal",
            "target_value": 70.0,
            "unit": "kg",
            "start_date": today.isoformat()
        }

        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/goals",
                json=goal_data,
                headers=auth_headers,
                timeout=10.0
            )

            assert response.status_code == 201, f"Failed to create weight goal: {response.text}"
            data = response.json()
            assert data["type"] == "weight"

            # Cleanup
            client.delete(f"{API_V1}/goals/{data['id']}", headers=auth_headers)

            print(f"\n✅ Created weight goal")

    def test_create_exercise_goal(self, auth_headers):
        """Test creating an exercise goal."""
        today = date.today()
        goal_data = {
            "type": "exercise",
            "title": "Exercise 5 times per week",
            "target_value": 20.0,
            "unit": "workouts",
            "start_date": today.isoformat(),
            "end_date": (today + timedelta(days=30)).isoformat()
        }

        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/goals",
                json=goal_data,
                headers=auth_headers,
                timeout=10.0
            )

            assert response.status_code == 201, f"Failed to create exercise goal: {response.text}"
            data = response.json()
            assert data["type"] == "exercise"

            # Cleanup
            client.delete(f"{API_V1}/goals/{data['id']}", headers=auth_headers)

            print(f"\n✅ Created exercise goal")

    def test_create_water_goal(self, auth_headers):
        """Test creating a water intake goal."""
        today = date.today()
        goal_data = {
            "type": "water",
            "title": "Drink 2L of water daily",
            "target_value": 2.0,
            "unit": "liters",
            "start_date": today.isoformat()
        }

        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/goals",
                json=goal_data,
                headers=auth_headers,
                timeout=10.0
            )

            assert response.status_code == 201, f"Failed to create water goal: {response.text}"
            data = response.json()
            assert data["type"] == "water"

            # Cleanup
            client.delete(f"{API_V1}/goals/{data['id']}", headers=auth_headers)

            print(f"\n✅ Created water goal")

    def test_create_sleep_goal(self, auth_headers):
        """Test creating a sleep goal."""
        today = date.today()
        goal_data = {
            "type": "sleep",
            "title": "Sleep 8 hours per night",
            "target_value": 8.0,
            "unit": "hours",
            "start_date": today.isoformat()
        }

        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/goals",
                json=goal_data,
                headers=auth_headers,
                timeout=10.0
            )

            assert response.status_code == 201, f"Failed to create sleep goal: {response.text}"
            data = response.json()
            assert data["type"] == "sleep"

            # Cleanup
            client.delete(f"{API_V1}/goals/{data['id']}", headers=auth_headers)

            print(f"\n✅ Created sleep goal")

    def test_create_calories_goal(self, auth_headers):
        """Test creating a calories goal."""
        today = date.today()
        goal_data = {
            "type": "calories",
            "title": "Daily calorie target",
            "target_value": 2000.0,
            "unit": "kcal",
            "start_date": today.isoformat()
        }

        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/goals",
                json=goal_data,
                headers=auth_headers,
                timeout=10.0
            )

            assert response.status_code == 201, f"Failed to create calories goal: {response.text}"
            data = response.json()
            assert data["type"] == "calories"

            # Cleanup
            client.delete(f"{API_V1}/goals/{data['id']}", headers=auth_headers)

            print(f"\n✅ Created calories goal")


# ===========================
# AUTHENTICATION TESTS
# ===========================

class TestGoalAuthentication:
    """Test authentication requirements for goal endpoints."""

    def test_create_goal_requires_auth(self):
        """Test that POST /api/v1/goals requires authentication."""
        goal_data = {
            "type": "weight",
            "title": "Test goal",
            "target_value": 70.0,
            "start_date": date.today().isoformat()
        }

        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/goals",
                json=goal_data,
                timeout=10.0
            )

            assert response.status_code in [401, 403], \
                f"Should require auth, got {response.status_code}"

            print("\n✅ Create goal endpoint requires authentication")

    def test_get_goals_requires_auth(self):
        """Test that GET /api/v1/goals requires authentication."""
        with httpx.Client() as client:
            response = client.get(
                f"{API_V1}/goals",
                timeout=10.0
            )

            assert response.status_code in [401, 403], \
                f"Should require auth, got {response.status_code}"

            print("\n✅ Get goals endpoint requires authentication")

    def test_get_goal_requires_auth(self):
        """Test that GET /api/v1/goals/{goal_id} requires authentication."""
        with httpx.Client() as client:
            response = client.get(
                f"{API_V1}/goals/1",
                timeout=10.0
            )

            assert response.status_code in [401, 403], \
                f"Should require auth, got {response.status_code}"

            print("\n✅ Get goal endpoint requires authentication")

    def test_update_goal_requires_auth(self):
        """Test that PUT /api/v1/goals/{goal_id} requires authentication."""
        update_data = {
            "current_value": 75.0
        }

        with httpx.Client() as client:
            response = client.put(
                f"{API_V1}/goals/1",
                json=update_data,
                timeout=10.0
            )

            assert response.status_code in [401, 403], \
                f"Should require auth, got {response.status_code}"

            print("\n✅ Update goal endpoint requires authentication")

    def test_delete_goal_requires_auth(self):
        """Test that DELETE /api/v1/goals/{goal_id} requires authentication."""
        with httpx.Client() as client:
            response = client.delete(
                f"{API_V1}/goals/1",
                timeout=10.0
            )

            assert response.status_code in [401, 403], \
                f"Should require auth, got {response.status_code}"

            print("\n✅ Delete goal endpoint requires authentication")


# ===========================
# AUTHORIZATION TESTS
# ===========================

class TestGoalAuthorization:
    """Test authorization - users can only access their own goals."""

    def test_cannot_access_other_user_goal(self, auth_headers):
        """Test that users cannot access goals from other users."""
        # Create a goal with first user
        today = date.today()
        goal_data = {
            "type": "weight",
            "title": "User 1 goal",
            "target_value": 70.0,
            "start_date": today.isoformat()
        }

        with httpx.Client() as client:
            # Create goal with user 1
            response = client.post(
                f"{API_V1}/goals",
                json=goal_data,
                headers=auth_headers,
                timeout=10.0
            )
            assert response.status_code == 201
            goal_id = response.json()["id"]

            # Create second user
            timestamp = str(int(datetime.now().timestamp()))
            user2_email = f"testgoals2{timestamp}@example.com"
            user2_username = f"testgoals2{timestamp}"

            client.post(
                f"{API_V1}/auth/register",
                json={
                    "email": user2_email,
                    "username": user2_username,
                    "password": _test_user_password,
                    "full_name": "Test User 2"
                }
            )

            # Login as user 2
            login_response = client.post(
                f"{API_V1}/auth/login",
                json={
                    "email": user2_email,
                    "password": _test_user_password
                }
            )
            user2_token = login_response.json()["access_token"]
            user2_headers = {"Authorization": f"Bearer {user2_token}"}

            # Try to access user 1's goal as user 2
            response = client.get(
                f"{API_V1}/goals/{goal_id}",
                headers=user2_headers,
                timeout=10.0
            )

            assert response.status_code == 403, \
                f"User 2 should not access User 1's goal, got {response.status_code}"

            # Cleanup
            client.delete(f"{API_V1}/goals/{goal_id}", headers=auth_headers)

            print("\n✅ Authorization properly enforced")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
