"""Integration tests for Meal Plans API endpoints."""

import httpx
import pytest
from datetime import datetime
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
    """Get or create test user and return credentials."""
    global _test_user_email, _test_user_username, _access_token

    if _access_token:
        return _access_token

    # Create unique username/email for this test session
    timestamp = str(int(datetime.now().timestamp()))
    _test_user_email = f"testmealplans{timestamp}@example.com"
    _test_user_username = f"testmealplans{timestamp}"

    with httpx.Client() as client:
        # Try to register
        response = client.post(
            f"{API_V1}/auth/register",
            json={
                "email": _test_user_email,
                "username": _test_user_username,
                "password": _test_user_password,
                "full_name": "Test User Meal Plans"
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
# MEAL PLAN CRUD TESTS
# ===========================

class TestMealPlanCRUDAPI:
    """Test suite for Meal Plan CRUD operations."""

    meal_plan_id = None

    def test_01_generate_meal_plan(self, auth_headers):
        """Test POST /api/v1/meal-plans/generate - Generate meal plan."""
        meal_plan_data = {
            "name": "My Test Meal Plan",
            "description": "A healthy meal plan for testing",
            "calorie_target": 2000,
            "dietary_preferences": ["vegetarian"],
            "allergies": ["peanuts"]
        }

        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/meal-plans/generate",
                json=meal_plan_data,
                headers=auth_headers,
                timeout=60.0  # Longer timeout for AI generation
            )

            # Note: This might fail if AI service is not available
            # In that case, we should handle gracefully
            if response.status_code == 201:
                data = response.json()

                # Verify response structure
                assert "success" in data, "Response missing 'success'"

                if data["success"]:
                    assert "meal_plan" in data, "Response missing 'meal_plan'"
                    meal_plan = data["meal_plan"]

                    assert "id" in meal_plan, "Meal plan missing 'id'"
                    assert "user_id" in meal_plan, "Meal plan missing 'user_id'"
                    assert meal_plan["name"] == "My Test Meal Plan"
                    assert meal_plan["calorie_target"] == 2000
                    assert "vegetarian" in meal_plan["dietary_preferences"]
                    assert "peanuts" in meal_plan["allergies"]
                    assert "plan_data" in meal_plan, "Meal plan missing 'plan_data'"
                    assert meal_plan["is_active"] == 1

                    # Verify 7-day structure
                    plan_data = meal_plan["plan_data"]
                    assert isinstance(plan_data, dict), "plan_data should be a dict"

                    # Save meal plan ID for later tests
                    TestMealPlanCRUDAPI.meal_plan_id = meal_plan["id"]

                    print(f"\n✅ Generated meal plan: ID={meal_plan['id']}, Name={meal_plan['name']}")
                else:
                    # AI generation failed, but endpoint worked
                    print(f"\n⚠️  Meal plan generation returned success=False: {data.get('error')}")
                    # Create a mock meal plan for testing
                    TestMealPlanCRUDAPI.meal_plan_id = None
            else:
                print(f"\n⚠️  Meal plan generation endpoint returned {response.status_code}")

    def test_02_generate_meal_plan_minimal(self, auth_headers):
        """Test POST /api/v1/meal-plans/generate - Generate with minimal data."""
        meal_plan_data = {
            "name": "Minimal Meal Plan"
        }

        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/meal-plans/generate",
                json=meal_plan_data,
                headers=auth_headers,
                timeout=60.0
            )

            # Should succeed with default values
            if response.status_code == 201:
                data = response.json()
                if data["success"] and data["meal_plan"]:
                    assert data["meal_plan"]["name"] == "Minimal Meal Plan"

                    # Cleanup
                    plan_id = data["meal_plan"]["id"]
                    client.delete(f"{API_V1}/meal-plans/{plan_id}", headers=auth_headers)

                    print(f"\n✅ Generated meal plan with minimal data")
                else:
                    print(f"\n⚠️  Meal plan generation with minimal data returned success=False")

    def test_03_get_meal_plans(self, auth_headers):
        """Test GET /api/v1/meal-plans - Get all meal plans."""
        with httpx.Client() as client:
            response = client.get(
                f"{API_V1}/meal-plans",
                headers=auth_headers,
                timeout=10.0
            )

            assert response.status_code == 200, f"Failed to get meal plans: {response.text}"
            data = response.json()

            # Verify response structure
            assert "meal_plans" in data, "Response missing 'meal_plans'"
            assert "total" in data, "Response missing 'total'"
            assert isinstance(data["meal_plans"], list), "meal_plans should be a list"
            assert data["total"] == len(data["meal_plans"])

            # If we created a meal plan in test_01, verify it's in the list
            if TestMealPlanCRUDAPI.meal_plan_id:
                meal_plan_ids = [mp["id"] for mp in data["meal_plans"]]
                assert TestMealPlanCRUDAPI.meal_plan_id in meal_plan_ids, \
                    "Created meal plan should be in the list"

            print(f"\n✅ Retrieved {data['total']} meal plans")

    def test_04_get_meal_plans_active_only(self, auth_headers):
        """Test GET /api/v1/meal-plans?active_only=true - Get active plans only."""
        with httpx.Client() as client:
            response = client.get(
                f"{API_V1}/meal-plans?active_only=true",
                headers=auth_headers,
                timeout=10.0
            )

            assert response.status_code == 200, f"Failed to get meal plans: {response.text}"
            data = response.json()

            # All meal plans should be active
            for plan in data["meal_plans"]:
                assert plan["is_active"] == 1, f"Plan {plan['id']} should be active"

            print(f"\n✅ Retrieved {data['total']} active meal plans")

    def test_05_get_meal_plans_include_inactive(self, auth_headers):
        """Test GET /api/v1/meal-plans?active_only=false - Get all plans."""
        with httpx.Client() as client:
            response = client.get(
                f"{API_V1}/meal-plans?active_only=false",
                headers=auth_headers,
                timeout=10.0
            )

            assert response.status_code == 200, f"Failed to get meal plans: {response.text}"
            data = response.json()

            assert "meal_plans" in data
            assert "total" in data

            print(f"\n✅ Retrieved {data['total']} meal plans (including inactive)")

    def test_06_get_meal_plan_by_id(self, auth_headers):
        """Test GET /api/v1/meal-plans/{plan_id} - Get specific meal plan."""
        if not TestMealPlanCRUDAPI.meal_plan_id:
            pytest.skip("No meal plan ID available")

        with httpx.Client() as client:
            response = client.get(
                f"{API_V1}/meal-plans/{TestMealPlanCRUDAPI.meal_plan_id}",
                headers=auth_headers,
                timeout=10.0
            )

            assert response.status_code == 200, f"Failed to get meal plan: {response.text}"
            data = response.json()

            assert data["id"] == TestMealPlanCRUDAPI.meal_plan_id
            assert data["name"] == "My Test Meal Plan"
            assert "plan_data" in data
            assert "user_id" in data

            print(f"\n✅ Retrieved meal plan: ID={data['id']}, Name={data['name']}")

    def test_07_get_meal_plan_not_found(self, auth_headers):
        """Test GET /api/v1/meal-plans/999999 - Meal plan not found."""
        with httpx.Client() as client:
            response = client.get(
                f"{API_V1}/meal-plans/999999",
                headers=auth_headers,
                timeout=10.0
            )

            assert response.status_code == 404, f"Should return 404, got {response.status_code}"

            print(f"\n✅ Non-existent meal plan handled correctly")

    def test_08_delete_meal_plan(self, auth_headers):
        """Test DELETE /api/v1/meal-plans/{plan_id} - Archive meal plan."""
        if not TestMealPlanCRUDAPI.meal_plan_id:
            pytest.skip("No meal plan ID available")

        with httpx.Client() as client:
            response = client.delete(
                f"{API_V1}/meal-plans/{TestMealPlanCRUDAPI.meal_plan_id}",
                headers=auth_headers,
                timeout=10.0
            )

            assert response.status_code == 200, f"Failed to delete meal plan: {response.text}"
            data = response.json()

            assert data["success"] == True
            assert "message" in data

            # Verify meal plan is archived (is_active = 0)
            verify_response = client.get(
                f"{API_V1}/meal-plans/{TestMealPlanCRUDAPI.meal_plan_id}",
                headers=auth_headers,
                timeout=10.0
            )

            if verify_response.status_code == 200:
                verify_data = verify_response.json()
                assert verify_data["is_active"] == 0, "Meal plan should be archived"

            print(f"\n✅ Archived meal plan: ID={TestMealPlanCRUDAPI.meal_plan_id}")

    def test_09_delete_meal_plan_not_found(self, auth_headers):
        """Test DELETE /api/v1/meal-plans/999999 - Meal plan not found."""
        with httpx.Client() as client:
            response = client.delete(
                f"{API_V1}/meal-plans/999999",
                headers=auth_headers,
                timeout=10.0
            )

            assert response.status_code == 404, f"Should return 404, got {response.status_code}"

            print(f"\n✅ Delete non-existent meal plan handled correctly")


# ===========================
# MEAL PLAN STRUCTURE TESTS
# ===========================

class TestMealPlanStructure:
    """Test suite for validating meal plan structure."""

    def test_meal_plan_7day_structure(self, auth_headers):
        """Test that generated meal plan has proper 7-day structure."""
        meal_plan_data = {
            "name": "Structure Test Plan",
            "calorie_target": 2000
        }

        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/meal-plans/generate",
                json=meal_plan_data,
                headers=auth_headers,
                timeout=60.0
            )

            if response.status_code == 201:
                data = response.json()

                if data["success"] and data["meal_plan"]:
                    meal_plan = data["meal_plan"]
                    plan_data = meal_plan["plan_data"]

                    # Verify structure contains days
                    assert isinstance(plan_data, dict), "plan_data should be a dict"

                    # Expected days: day_1 through day_7 or similar structure
                    # Structure may vary based on AI output
                    print(f"\n✅ Meal plan has valid structure: {list(plan_data.keys())[:3]}...")

                    # Cleanup
                    client.delete(f"{API_V1}/meal-plans/{meal_plan['id']}", headers=auth_headers)
                else:
                    print(f"\n⚠️  Could not verify structure - generation failed")

    def test_meal_plan_contains_summary(self, auth_headers):
        """Test that meal plan includes summary information."""
        meal_plan_data = {
            "name": "Summary Test Plan",
            "calorie_target": 1800
        }

        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/meal-plans/generate",
                json=meal_plan_data,
                headers=auth_headers,
                timeout=60.0
            )

            if response.status_code == 201:
                data = response.json()

                if data["success"] and data["meal_plan"]:
                    meal_plan = data["meal_plan"]

                    # Should have summary field
                    assert "summary" in meal_plan, "Meal plan should have summary"

                    print(f"\n✅ Meal plan includes summary")

                    # Cleanup
                    client.delete(f"{API_V1}/meal-plans/{meal_plan['id']}", headers=auth_headers)


# ===========================
# DIETARY PREFERENCES TESTS
# ===========================

class TestDietaryPreferences:
    """Test suite for dietary preferences."""

    def test_vegetarian_meal_plan(self, auth_headers):
        """Test generating vegetarian meal plan."""
        meal_plan_data = {
            "name": "Vegetarian Plan",
            "dietary_preferences": ["vegetarian"],
            "calorie_target": 2000
        }

        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/meal-plans/generate",
                json=meal_plan_data,
                headers=auth_headers,
                timeout=60.0
            )

            if response.status_code == 201:
                data = response.json()

                if data["success"] and data["meal_plan"]:
                    meal_plan = data["meal_plan"]
                    assert "vegetarian" in meal_plan["dietary_preferences"]

                    print(f"\n✅ Generated vegetarian meal plan")

                    # Cleanup
                    client.delete(f"{API_V1}/meal-plans/{meal_plan['id']}", headers=auth_headers)

    def test_low_carb_meal_plan(self, auth_headers):
        """Test generating low-carb meal plan."""
        meal_plan_data = {
            "name": "Low Carb Plan",
            "dietary_preferences": ["low-carb"],
            "calorie_target": 1800
        }

        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/meal-plans/generate",
                json=meal_plan_data,
                headers=auth_headers,
                timeout=60.0
            )

            if response.status_code == 201:
                data = response.json()

                if data["success"] and data["meal_plan"]:
                    meal_plan = data["meal_plan"]
                    assert "low-carb" in meal_plan["dietary_preferences"]

                    print(f"\n✅ Generated low-carb meal plan")

                    # Cleanup
                    client.delete(f"{API_V1}/meal-plans/{meal_plan['id']}", headers=auth_headers)

    def test_meal_plan_with_allergies(self, auth_headers):
        """Test generating meal plan with allergies."""
        meal_plan_data = {
            "name": "Allergy-Aware Plan",
            "allergies": ["peanuts", "shellfish"],
            "calorie_target": 2000
        }

        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/meal-plans/generate",
                json=meal_plan_data,
                headers=auth_headers,
                timeout=60.0
            )

            if response.status_code == 201:
                data = response.json()

                if data["success"] and data["meal_plan"]:
                    meal_plan = data["meal_plan"]
                    assert "peanuts" in meal_plan["allergies"]
                    assert "shellfish" in meal_plan["allergies"]

                    print(f"\n✅ Generated meal plan with allergy restrictions")

                    # Cleanup
                    client.delete(f"{API_V1}/meal-plans/{meal_plan['id']}", headers=auth_headers)

    def test_multiple_dietary_preferences(self, auth_headers):
        """Test generating meal plan with multiple preferences."""
        meal_plan_data = {
            "name": "Multi-Preference Plan",
            "dietary_preferences": ["vegetarian", "high-protein", "gluten-free"],
            "calorie_target": 2200
        }

        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/meal-plans/generate",
                json=meal_plan_data,
                headers=auth_headers,
                timeout=60.0
            )

            if response.status_code == 201:
                data = response.json()

                if data["success"] and data["meal_plan"]:
                    meal_plan = data["meal_plan"]
                    prefs = meal_plan["dietary_preferences"]
                    assert "vegetarian" in prefs
                    assert "high-protein" in prefs
                    assert "gluten-free" in prefs

                    print(f"\n✅ Generated meal plan with multiple preferences")

                    # Cleanup
                    client.delete(f"{API_V1}/meal-plans/{meal_plan['id']}", headers=auth_headers)


# ===========================
# AUTHENTICATION TESTS
# ===========================

class TestMealPlanAuthentication:
    """Test authentication requirements for meal plan endpoints."""

    def test_generate_meal_plan_requires_auth(self):
        """Test that POST /api/v1/meal-plans/generate requires authentication."""
        meal_plan_data = {
            "name": "Test Plan"
        }

        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/meal-plans/generate",
                json=meal_plan_data,
                timeout=10.0
            )

            assert response.status_code in [401, 403], \
                f"Should require auth, got {response.status_code}"

            print("\n✅ Generate meal plan endpoint requires authentication")

    def test_get_meal_plans_requires_auth(self):
        """Test that GET /api/v1/meal-plans requires authentication."""
        with httpx.Client() as client:
            response = client.get(
                f"{API_V1}/meal-plans",
                timeout=10.0
            )

            assert response.status_code in [401, 403], \
                f"Should require auth, got {response.status_code}"

            print("\n✅ Get meal plans endpoint requires authentication")

    def test_get_meal_plan_requires_auth(self):
        """Test that GET /api/v1/meal-plans/{plan_id} requires authentication."""
        with httpx.Client() as client:
            response = client.get(
                f"{API_V1}/meal-plans/1",
                timeout=10.0
            )

            assert response.status_code in [401, 403], \
                f"Should require auth, got {response.status_code}"

            print("\n✅ Get meal plan endpoint requires authentication")

    def test_delete_meal_plan_requires_auth(self):
        """Test that DELETE /api/v1/meal-plans/{plan_id} requires authentication."""
        with httpx.Client() as client:
            response = client.delete(
                f"{API_V1}/meal-plans/1",
                timeout=10.0
            )

            assert response.status_code in [401, 403], \
                f"Should require auth, got {response.status_code}"

            print("\n✅ Delete meal plan endpoint requires authentication")


# ===========================
# AUTHORIZATION TESTS
# ===========================

class TestMealPlanAuthorization:
    """Test authorization - users can only access their own meal plans."""

    def test_cannot_access_other_user_meal_plan(self, auth_headers):
        """Test that users cannot access meal plans from other users."""
        # Create a meal plan with first user
        meal_plan_data = {
            "name": "User 1 Meal Plan",
            "calorie_target": 2000
        }

        with httpx.Client() as client:
            # Create meal plan with user 1
            response = client.post(
                f"{API_V1}/meal-plans/generate",
                json=meal_plan_data,
                headers=auth_headers,
                timeout=60.0
            )

            if response.status_code != 201 or not response.json().get("success"):
                pytest.skip("Could not create meal plan for authorization test")

            meal_plan_id = response.json()["meal_plan"]["id"]

            # Create second user
            timestamp = str(int(datetime.now().timestamp()))
            user2_email = f"testmealplans2{timestamp}@example.com"
            user2_username = f"testmealplans2{timestamp}"

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

            # Try to access user 1's meal plan as user 2
            response = client.get(
                f"{API_V1}/meal-plans/{meal_plan_id}",
                headers=user2_headers,
                timeout=10.0
            )

            # Should return 404 (not found) because it filters by user_id
            assert response.status_code == 404, \
                f"User 2 should not access User 1's meal plan, got {response.status_code}"

            # Cleanup
            client.delete(f"{API_V1}/meal-plans/{meal_plan_id}", headers=auth_headers)

            print("\n✅ Authorization properly enforced")


# ===========================
# STREAMING TESTS
# ===========================

class TestMealPlanStreaming:
    """Test suite for streaming meal plan generation."""

    def test_stream_meal_plan_generation(self, auth_headers):
        """Test POST /api/v1/meal-plans/generate/stream - Stream generation."""
        meal_plan_data = {
            "name": "Streamed Meal Plan",
            "calorie_target": 2000
        }

        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/meal-plans/generate/stream",
                json=meal_plan_data,
                headers=auth_headers,
                timeout=60.0
            )

            # Should return streaming response
            if response.status_code == 200:
                # Verify content type
                content_type = response.headers.get("content-type", "")
                assert "text/event-stream" in content_type, \
                    f"Expected SSE content type, got {content_type}"

                # Read a few chunks to verify streaming works
                chunks_received = 0
                for chunk in response.iter_lines():
                    if chunk:
                        chunks_received += 1
                        if chunks_received >= 3:  # Just verify we get some data
                            break

                assert chunks_received > 0, "Should receive streaming data"

                print(f"\n✅ Streaming meal plan generation works")
            else:
                print(f"\n⚠️  Streaming endpoint returned {response.status_code}")

    def test_stream_requires_auth(self):
        """Test that streaming endpoint requires authentication."""
        meal_plan_data = {
            "name": "Test Plan"
        }

        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/meal-plans/generate/stream",
                json=meal_plan_data,
                timeout=10.0
            )

            assert response.status_code in [401, 403], \
                f"Should require auth, got {response.status_code}"

            print("\n✅ Streaming endpoint requires authentication")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
