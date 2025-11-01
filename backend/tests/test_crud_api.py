"""Integration tests for Meal, Exercise, and Water CRUD API endpoints."""

import httpx
import pytest
from datetime import date, datetime, time
import json

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
    """Get or create test user and return credentials."""
    global _test_user_email, _test_user_username, _access_token
    
    if _access_token:
        return _access_token
    
    # Create unique username/email for this test session
    timestamp = str(int(datetime.now().timestamp()))
    _test_user_email = f"testcrud{timestamp}@example.com"
    _test_user_username = f"testcrud{timestamp}"
    
    with httpx.Client() as client:
        # Try to register
        response = client.post(
            f"{API_V1}/auth/register",
            json={
                "email": _test_user_email,
                "username": _test_user_username,
                "password": _test_user_password,
                "full_name": "Test User CRUD"
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


def get_or_create_test_day(auth_headers):
    """Get or create a test day for CRUD operations."""
    global _test_day_id
    
    if _test_day_id:
        return _test_day_id
    
    today = date.today().isoformat()
    
    with httpx.Client() as client:
        response = client.post(
            f"{API_V1}/days",
            json={"date": today},
            headers=auth_headers,
            timeout=10.0
        )
        
        assert response.status_code == 201, f"Failed to create day: {response.text}"
        data = response.json()
        _test_day_id = data["id"]
        
        return _test_day_id


@pytest.fixture
def auth_headers():
    """Get authorization headers with access token."""
    token = get_or_create_test_user()
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_day_id(auth_headers):
    """Get test day ID."""
    return get_or_create_test_day(auth_headers)


# ===========================
# MEAL MODULE TESTS
# ===========================

class TestMealCRUDAPI:
    """Test suite for Meal CRUD operations."""
    
    meal_id = None
    
    def test_01_create_meal(self, auth_headers, test_day_id):
        """Test POST /api/v1/days/{day_id}/meals - Create meal."""
        meal_data = {
            "category": "breakfast",
            "calories": 450.5,
            "protein": 25.0,
            "carbs": 50.0,
            "fat": 15.0,
            "fiber": 5.0,
            "sugar": 10.0,
            "sodium": 300.0,
            "notes": "Oatmeal with fruits and nuts",
            "day_id": test_day_id
        }
        
        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/days/{test_day_id}/meals",
                json=meal_data,
                headers=auth_headers,
                timeout=10.0
            )
            
            assert response.status_code == 201, f"Failed to create meal: {response.text}"
            data = response.json()
            
            # Verify response structure
            assert "id" in data, "Response missing 'id'"
            assert "day_id" in data, "Response missing 'day_id'"
            assert data["day_id"] == test_day_id
            assert data["category"] == "breakfast"
            assert float(data["calories"]) == 450.5
            assert data["notes"] == "Oatmeal with fruits and nuts"
            
            # Save meal ID for later tests
            TestMealCRUDAPI.meal_id = data["id"]
            
            print(f"\n✅ Created meal: ID={data['id']}, Category={data['category']}")
    
    def test_02_get_meals_by_day(self, auth_headers, test_day_id):
        """Test GET /api/v1/days/{day_id}/meals - Get all meals for a day."""
        with httpx.Client() as client:
            response = client.get(
                f"{API_V1}/days/{test_day_id}/meals",
                headers=auth_headers,
                timeout=10.0
            )
            
            assert response.status_code == 200, f"Failed to get meals: {response.text}"
            data = response.json()
            
            assert isinstance(data, list), "Response should be a list"
            assert len(data) >= 1, "Should have at least one meal"
            
            # Verify our created meal is in the list
            meal_ids = [m["id"] for m in data]
            assert TestMealCRUDAPI.meal_id in meal_ids, "Created meal should be in the list"
            
            print(f"\n✅ Retrieved {len(data)} meals for day {test_day_id}")
    
    def test_03_get_meal_by_id(self, auth_headers):
        """Test GET /api/v1/meals/{meal_id} - Get specific meal."""
        assert TestMealCRUDAPI.meal_id is not None, "No meal ID available"
        
        with httpx.Client() as client:
            response = client.get(
                f"{API_V1}/meals/{TestMealCRUDAPI.meal_id}",
                headers=auth_headers,
                timeout=10.0
            )
            
            assert response.status_code == 200, f"Failed to get meal: {response.text}"
            data = response.json()
            
            assert data["id"] == TestMealCRUDAPI.meal_id
            assert data["category"] == "breakfast"
            assert float(data["calories"]) == 450.5
            
            print(f"\n✅ Retrieved meal: ID={data['id']}, Category={data['category']}")
    
    def test_04_update_meal(self, auth_headers):
        """Test PUT /api/v1/meals/{meal_id} - Update meal."""
        assert TestMealCRUDAPI.meal_id is not None, "No meal ID available"
        
        update_data = {
            "calories": 500.0,
            "notes": "Updated: Oatmeal with extra fruits"
        }
        
        with httpx.Client() as client:
            response = client.put(
                f"{API_V1}/meals/{TestMealCRUDAPI.meal_id}",
                json=update_data,
                headers=auth_headers,
                timeout=10.0
            )
            
            assert response.status_code == 200, f"Failed to update meal: {response.text}"
            data = response.json()
            
            assert float(data["calories"]) == 500.0
            assert data["notes"] == "Updated: Oatmeal with extra fruits"
            
            print(f"\n✅ Updated meal: ID={data['id']}, Calories={data['calories']}")
    
    def test_05_delete_meal(self, auth_headers):
        """Test DELETE /api/v1/meals/{meal_id} - Delete meal."""
        assert TestMealCRUDAPI.meal_id is not None, "No meal ID available"
        
        with httpx.Client() as client:
            response = client.delete(
                f"{API_V1}/meals/{TestMealCRUDAPI.meal_id}",
                headers=auth_headers,
                timeout=10.0
            )
            
            assert response.status_code == 204, f"Failed to delete meal: {response.text}"
            
            # Verify meal is deleted
            verify_response = client.get(
                f"{API_V1}/meals/{TestMealCRUDAPI.meal_id}",
                headers=auth_headers,
                timeout=10.0
            )
            
            assert verify_response.status_code == 404, "Meal should be deleted"
            
            print(f"\n✅ Deleted meal: ID={TestMealCRUDAPI.meal_id}")


# ===========================
# EXERCISE MODULE TESTS
# ===========================

class TestExerciseCRUDAPI:
    """Test suite for Exercise CRUD operations."""
    
    exercise_id = None
    
    def test_01_create_exercise(self, auth_headers, test_day_id):
        """Test POST /api/v1/days/{day_id}/exercises - Create exercise."""
        exercise_data = {
            "type": "running",
            "name": "Morning run",
            "start_time": datetime.now().isoformat(),
            "duration": 1800,  # 30 minutes in seconds
            "distance": 5.0,
            "calories_burned": 350.0,
            "heart_rate_avg": 145,
            "heart_rate_max": 165,
            "intensity": 4,
            "notes": "Great morning run at the park"
        }
        
        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/days/{test_day_id}/exercises",
                json=exercise_data,
                headers=auth_headers,
                timeout=10.0
            )
            
            assert response.status_code == 201, f"Failed to create exercise: {response.text}"
            data = response.json()
            
            # Verify response structure
            assert "id" in data, "Response missing 'id'"
            assert "day_id" in data, "Response missing 'day_id'"
            assert data["day_id"] == test_day_id
            assert data["type"] == "running"
            assert data["name"] == "Morning run"
            assert data["duration"] == 1800
            assert float(data["distance"]) == 5.0
            
            # Save exercise ID for later tests
            TestExerciseCRUDAPI.exercise_id = data["id"]
            
            print(f"\n✅ Created exercise: ID={data['id']}, Type={data['type']}")
    
    def test_02_get_exercises_by_day(self, auth_headers, test_day_id):
        """Test GET /api/v1/days/{day_id}/exercises - Get all exercises for a day."""
        with httpx.Client() as client:
            response = client.get(
                f"{API_V1}/days/{test_day_id}/exercises",
                headers=auth_headers,
                timeout=10.0
            )
            
            assert response.status_code == 200, f"Failed to get exercises: {response.text}"
            data = response.json()
            
            assert isinstance(data, list), "Response should be a list"
            assert len(data) >= 1, "Should have at least one exercise"
            
            # Verify our created exercise is in the list
            exercise_ids = [e["id"] for e in data]
            assert TestExerciseCRUDAPI.exercise_id in exercise_ids, "Created exercise should be in the list"
            
            print(f"\n✅ Retrieved {len(data)} exercises for day {test_day_id}")
    
    def test_03_get_exercise_by_id(self, auth_headers):
        """Test GET /api/v1/exercises/{exercise_id} - Get specific exercise."""
        assert TestExerciseCRUDAPI.exercise_id is not None, "No exercise ID available"
        
        with httpx.Client() as client:
            response = client.get(
                f"{API_V1}/exercises/{TestExerciseCRUDAPI.exercise_id}",
                headers=auth_headers,
                timeout=10.0
            )
            
            assert response.status_code == 200, f"Failed to get exercise: {response.text}"
            data = response.json()
            
            assert data["id"] == TestExerciseCRUDAPI.exercise_id
            assert data["type"] == "running"
            assert data["name"] == "Morning run"
            
            print(f"\n✅ Retrieved exercise: ID={data['id']}, Type={data['type']}")
    
    def test_04_update_exercise(self, auth_headers):
        """Test PUT /api/v1/exercises/{exercise_id} - Update exercise."""
        assert TestExerciseCRUDAPI.exercise_id is not None, "No exercise ID available"
        
        update_data = {
            "duration": 2100,  # Updated to 35 minutes
            "distance": 5.5,
            "notes": "Updated: Extended the run by 5 minutes"
        }
        
        with httpx.Client() as client:
            response = client.put(
                f"{API_V1}/exercises/{TestExerciseCRUDAPI.exercise_id}",
                json=update_data,
                headers=auth_headers,
                timeout=10.0
            )
            
            assert response.status_code == 200, f"Failed to update exercise: {response.text}"
            data = response.json()
            
            assert data["duration"] == 2100
            assert float(data["distance"]) == 5.5
            assert data["notes"] == "Updated: Extended the run by 5 minutes"
            
            print(f"\n✅ Updated exercise: ID={data['id']}, Duration={data['duration']}s")
    
    def test_05_delete_exercise(self, auth_headers):
        """Test DELETE /api/v1/exercises/{exercise_id} - Delete exercise."""
        assert TestExerciseCRUDAPI.exercise_id is not None, "No exercise ID available"
        
        with httpx.Client() as client:
            response = client.delete(
                f"{API_V1}/exercises/{TestExerciseCRUDAPI.exercise_id}",
                headers=auth_headers,
                timeout=10.0
            )
            
            assert response.status_code == 204, f"Failed to delete exercise: {response.text}"
            
            # Verify exercise is deleted
            verify_response = client.get(
                f"{API_V1}/exercises/{TestExerciseCRUDAPI.exercise_id}",
                headers=auth_headers,
                timeout=10.0
            )
            
            assert verify_response.status_code == 404, "Exercise should be deleted"
            
            print(f"\n✅ Deleted exercise: ID={TestExerciseCRUDAPI.exercise_id}")


# ===========================
# WATER MODULE TESTS
# ===========================

class TestWaterCRUDAPI:
    """Test suite for Water CRUD operations."""
    
    water_id = None
    
    def test_01_create_water(self, auth_headers, test_day_id):
        """Test POST /api/v1/days/{day_id}/water - Create water intake."""
        water_data = {
            "amount": 0.5,  # 500ml in liters
            "time": datetime.now().isoformat()
        }
        
        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/days/{test_day_id}/water",
                json=water_data,
                headers=auth_headers,
                timeout=10.0
            )
            
            assert response.status_code == 201, f"Failed to create water intake: {response.text}"
            data = response.json()
            
            # Verify response structure
            assert "id" in data, "Response missing 'id'"
            assert "day_id" in data, "Response missing 'day_id'"
            assert data["day_id"] == test_day_id
            assert float(data["amount"]) == 0.5
            
            # Save water ID for later tests
            TestWaterCRUDAPI.water_id = data["id"]
            
            print(f"\n✅ Created water intake: ID={data['id']}, Amount={data['amount']}L")
    
    def test_02_get_water_by_day(self, auth_headers, test_day_id):
        """Test GET /api/v1/days/{day_id}/water - Get all water intakes for a day."""
        with httpx.Client() as client:
            response = client.get(
                f"{API_V1}/days/{test_day_id}/water",
                headers=auth_headers,
                timeout=10.0
            )
            
            assert response.status_code == 200, f"Failed to get water intakes: {response.text}"
            data = response.json()
            
            assert isinstance(data, list), "Response should be a list"
            assert len(data) >= 1, "Should have at least one water intake"
            
            # Verify our created water intake is in the list
            water_ids = [w["id"] for w in data]
            assert TestWaterCRUDAPI.water_id in water_ids, "Created water intake should be in the list"
            
            print(f"\n✅ Retrieved {len(data)} water intakes for day {test_day_id}")
    
    def test_03_get_water_by_id(self, auth_headers):
        """Test GET /api/v1/water/{water_id} - Get specific water intake."""
        assert TestWaterCRUDAPI.water_id is not None, "No water ID available"
        
        with httpx.Client() as client:
            response = client.get(
                f"{API_V1}/water/{TestWaterCRUDAPI.water_id}",
                headers=auth_headers,
                timeout=10.0
            )
            
            assert response.status_code == 200, f"Failed to get water intake: {response.text}"
            data = response.json()
            
            assert data["id"] == TestWaterCRUDAPI.water_id
            assert float(data["amount"]) == 0.5
            
            print(f"\n✅ Retrieved water intake: ID={data['id']}, Amount={data['amount']}L")
    
    def test_04_update_water(self, auth_headers):
        """Test PUT /api/v1/water/{water_id} - Update water intake."""
        assert TestWaterCRUDAPI.water_id is not None, "No water ID available"
        
        update_data = {
            "amount": 0.75  # Updated to 750ml
        }
        
        with httpx.Client() as client:
            response = client.put(
                f"{API_V1}/water/{TestWaterCRUDAPI.water_id}",
                json=update_data,
                headers=auth_headers,
                timeout=10.0
            )
            
            assert response.status_code == 200, f"Failed to update water intake: {response.text}"
            data = response.json()
            
            assert float(data["amount"]) == 0.75
            
            print(f"\n✅ Updated water intake: ID={data['id']}, Amount={data['amount']}L")
    
    def test_05_delete_water(self, auth_headers):
        """Test DELETE /api/v1/water/{water_id} - Delete water intake."""
        assert TestWaterCRUDAPI.water_id is not None, "No water ID available"
        
        with httpx.Client() as client:
            response = client.delete(
                f"{API_V1}/water/{TestWaterCRUDAPI.water_id}",
                headers=auth_headers,
                timeout=10.0
            )
            
            assert response.status_code == 204, f"Failed to delete water intake: {response.text}"
            
            # Verify water intake is deleted
            verify_response = client.get(
                f"{API_V1}/water/{TestWaterCRUDAPI.water_id}",
                headers=auth_headers,
                timeout=10.0
            )
            
            assert verify_response.status_code == 404, "Water intake should be deleted"
            
            print(f"\n✅ Deleted water intake: ID={TestWaterCRUDAPI.water_id}")


# ===========================
# AUTHENTICATION TESTS
# ===========================

class TestAuthenticationRequirements:
    """Test authentication requirements for all endpoints."""
    
    def test_meal_endpoints_require_auth(self, test_day_id):
        """Test that meal endpoints require authentication."""
        with httpx.Client() as client:
            # Create without auth
            response = client.post(
                f"{API_V1}/days/{test_day_id}/meals",
                json={"category": "breakfast", "day_id": test_day_id},
                timeout=10.0
            )
            assert response.status_code in [401, 403], f"Should require auth, got {response.status_code}"
            
            # Get list without auth
            response = client.get(f"{API_V1}/days/{test_day_id}/meals", timeout=10.0)
            assert response.status_code in [401, 403], f"Should require auth, got {response.status_code}"
            
            print("\n✅ Meal endpoints properly require authentication")
    
    def test_exercise_endpoints_require_auth(self, test_day_id):
        """Test that exercise endpoints require authentication."""
        with httpx.Client() as client:
            # Create without auth
            response = client.post(
                f"{API_V1}/days/{test_day_id}/exercises",
                json={"type": "running"},
                timeout=10.0
            )
            assert response.status_code in [401, 403], f"Should require auth, got {response.status_code}"
            
            # Get list without auth
            response = client.get(f"{API_V1}/days/{test_day_id}/exercises", timeout=10.0)
            assert response.status_code in [401, 403], f"Should require auth, got {response.status_code}"
            
            print("\n✅ Exercise endpoints properly require authentication")
    
    def test_water_endpoints_require_auth(self, test_day_id):
        """Test that water endpoints require authentication."""
        with httpx.Client() as client:
            # Create without auth
            response = client.post(
                f"{API_V1}/days/{test_day_id}/water",
                json={"amount": 0.5},
                timeout=10.0
            )
            assert response.status_code in [401, 403], f"Should require auth, got {response.status_code}"
            
            # Get list without auth
            response = client.get(f"{API_V1}/days/{test_day_id}/water", timeout=10.0)
            assert response.status_code in [401, 403], f"Should require auth, got {response.status_code}"
            
            print("\n✅ Water endpoints properly require authentication")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
