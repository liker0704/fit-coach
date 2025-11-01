"""Integration tests for Sleep CRUD API endpoints."""

import httpx
import pytest
from datetime import date, datetime, timedelta
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
    _test_user_email = f"testsleep{timestamp}@example.com"
    _test_user_username = f"testsleep{timestamp}"
    
    with httpx.Client() as client:
        # Try to register
        response = client.post(
            f"{API_V1}/auth/register",
            json={
                "email": _test_user_email,
                "username": _test_user_username,
                "password": _test_user_password,
                "full_name": "Test User Sleep"
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
# SLEEP MODULE TESTS
# ===========================

class TestSleepCRUDAPI:
    """Test suite for Sleep CRUD operations."""
    
    sleep_id = None
    
    def test_01_create_sleep(self, auth_headers, test_day_id):
        """Test POST /api/v1/days/{day_id}/sleep - Create sleep record."""
        # Create a bedtime (last night 11 PM) and wake time (today 7 AM)
        now = datetime.now()
        bedtime = now.replace(hour=23, minute=0, second=0, microsecond=0) - timedelta(days=1)
        wake_time = now.replace(hour=7, minute=0, second=0, microsecond=0)
        
        sleep_data = {
            "bedtime": bedtime.isoformat(),
            "wake_time": wake_time.isoformat(),
            "duration": 8.0,  # 8 hours
            "quality": 4,  # 1-5 scale
            "deep_sleep": 2.5,  # hours
            "rem_sleep": 1.5,  # hours
            "interruptions": 2,
            "notes": "Good night's sleep with minimal interruptions",
            "day_id": test_day_id
        }
        
        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/days/{test_day_id}/sleep",
                json=sleep_data,
                headers=auth_headers,
                timeout=10.0
            )
            
            assert response.status_code == 201, f"Failed to create sleep record: {response.text}"
            data = response.json()
            
            # Verify response structure
            assert "id" in data, "Response missing 'id'"
            assert "day_id" in data, "Response missing 'day_id'"
            assert data["day_id"] == test_day_id
            assert data["duration"] == "8.0" or float(data["duration"]) == 8.0
            assert data["quality"] == 4
            assert data["interruptions"] == 2
            assert data["notes"] == "Good night's sleep with minimal interruptions"
            assert "created_at" in data, "Response missing 'created_at'"
            
            # Save sleep ID for later tests
            TestSleepCRUDAPI.sleep_id = data["id"]
            
            print(f"\n✅ Created sleep record: ID={data['id']}, Quality={data['quality']}")
    
    def test_02_get_sleep_by_day(self, auth_headers, test_day_id):
        """Test GET /api/v1/days/{day_id}/sleep - Get all sleep records for a day."""
        with httpx.Client() as client:
            response = client.get(
                f"{API_V1}/days/{test_day_id}/sleep",
                headers=auth_headers,
                timeout=10.0
            )
            
            assert response.status_code == 200, f"Failed to get sleep records: {response.text}"
            data = response.json()
            
            assert isinstance(data, list), "Response should be a list"
            assert len(data) >= 1, "Should have at least one sleep record"
            
            # Verify our created sleep record is in the list
            sleep_ids = [s["id"] for s in data]
            assert TestSleepCRUDAPI.sleep_id in sleep_ids, "Created sleep record should be in the list"
            
            print(f"\n✅ Retrieved {len(data)} sleep records for day {test_day_id}")
    
    def test_03_get_sleep_by_id(self, auth_headers):
        """Test GET /api/v1/sleep/{sleep_id} - Get specific sleep record."""
        assert TestSleepCRUDAPI.sleep_id is not None, "No sleep ID available"
        
        with httpx.Client() as client:
            response = client.get(
                f"{API_V1}/sleep/{TestSleepCRUDAPI.sleep_id}",
                headers=auth_headers,
                timeout=10.0
            )
            
            assert response.status_code == 200, f"Failed to get sleep record: {response.text}"
            data = response.json()
            
            assert data["id"] == TestSleepCRUDAPI.sleep_id
            assert data["quality"] == 4
            assert data["interruptions"] == 2
            assert "created_at" in data
            
            print(f"\n✅ Retrieved sleep record: ID={data['id']}, Quality={data['quality']}")
    
    def test_04_update_sleep(self, auth_headers):
        """Test PUT /api/v1/sleep/{sleep_id} - Update sleep record."""
        assert TestSleepCRUDAPI.sleep_id is not None, "No sleep ID available"
        
        update_data = {
            "quality": 5,  # Updated quality
            "interruptions": 1,  # Fewer interruptions
            "notes": "Updated: Excellent sleep quality"
        }
        
        with httpx.Client() as client:
            response = client.put(
                f"{API_V1}/sleep/{TestSleepCRUDAPI.sleep_id}",
                json=update_data,
                headers=auth_headers,
                timeout=10.0
            )
            
            assert response.status_code == 200, f"Failed to update sleep record: {response.text}"
            data = response.json()
            
            assert data["quality"] == 5
            assert data["interruptions"] == 1
            assert data["notes"] == "Updated: Excellent sleep quality"
            
            print(f"\n✅ Updated sleep record: ID={data['id']}, Quality={data['quality']}")
    
    def test_05_delete_sleep(self, auth_headers):
        """Test DELETE /api/v1/sleep/{sleep_id} - Delete sleep record."""
        assert TestSleepCRUDAPI.sleep_id is not None, "No sleep ID available"
        
        with httpx.Client() as client:
            response = client.delete(
                f"{API_V1}/sleep/{TestSleepCRUDAPI.sleep_id}",
                headers=auth_headers,
                timeout=10.0
            )
            
            assert response.status_code == 204, f"Failed to delete sleep record: {response.text}"
            
            # Verify sleep record is deleted
            verify_response = client.get(
                f"{API_V1}/sleep/{TestSleepCRUDAPI.sleep_id}",
                headers=auth_headers,
                timeout=10.0
            )
            
            assert verify_response.status_code == 404, "Sleep record should be deleted"
            
            print(f"\n✅ Deleted sleep record: ID={TestSleepCRUDAPI.sleep_id}")


# ===========================
# VALIDATION TESTS
# ===========================

class TestSleepValidation:
    """Test validation for Sleep endpoints."""
    
    def test_quality_validation_min(self, auth_headers, test_day_id):
        """Test that quality must be >= 1."""
        now = datetime.now()
        bedtime = now.replace(hour=23, minute=0, second=0, microsecond=0) - timedelta(days=1)
        wake_time = now.replace(hour=7, minute=0, second=0, microsecond=0)
        
        sleep_data = {
            "bedtime": bedtime.isoformat(),
            "wake_time": wake_time.isoformat(),
            "duration": 8.0,
            "quality": 0,  # Invalid: below minimum
            "day_id": test_day_id
        }
        
        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/days/{test_day_id}/sleep",
                json=sleep_data,
                headers=auth_headers,
                timeout=10.0
            )
            
            assert response.status_code == 422, f"Should fail validation, got {response.status_code}"
            
            print("\n✅ Quality validation (min) working correctly")
    
    def test_quality_validation_max(self, auth_headers, test_day_id):
        """Test that quality must be <= 5."""
        now = datetime.now()
        bedtime = now.replace(hour=23, minute=0, second=0, microsecond=0) - timedelta(days=1)
        wake_time = now.replace(hour=7, minute=0, second=0, microsecond=0)
        
        sleep_data = {
            "bedtime": bedtime.isoformat(),
            "wake_time": wake_time.isoformat(),
            "duration": 8.0,
            "quality": 6,  # Invalid: above maximum
            "day_id": test_day_id
        }
        
        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/days/{test_day_id}/sleep",
                json=sleep_data,
                headers=auth_headers,
                timeout=10.0
            )
            
            assert response.status_code == 422, f"Should fail validation, got {response.status_code}"
            
            print("\n✅ Quality validation (max) working correctly")
    
    def test_duration_validation_negative(self, auth_headers, test_day_id):
        """Test that duration cannot be negative."""
        now = datetime.now()
        bedtime = now.replace(hour=23, minute=0, second=0, microsecond=0) - timedelta(days=1)
        wake_time = now.replace(hour=7, minute=0, second=0, microsecond=0)
        
        sleep_data = {
            "bedtime": bedtime.isoformat(),
            "wake_time": wake_time.isoformat(),
            "duration": -1.0,  # Invalid: negative duration
            "quality": 4,
            "day_id": test_day_id
        }
        
        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/days/{test_day_id}/sleep",
                json=sleep_data,
                headers=auth_headers,
                timeout=10.0
            )
            
            assert response.status_code == 422, f"Should fail validation, got {response.status_code}"
            
            print("\n✅ Duration validation (negative) working correctly")


# ===========================
# AUTHORIZATION TESTS
# ===========================

class TestSleepAuthorization:
    """Test authorization requirements for Sleep endpoints."""
    
    def test_sleep_endpoints_require_auth(self, test_day_id):
        """Test that sleep endpoints require authentication."""
        with httpx.Client() as client:
            # Create without auth
            response = client.post(
                f"{API_V1}/days/{test_day_id}/sleep",
                json={"quality": 4, "day_id": test_day_id},
                timeout=10.0
            )
            assert response.status_code in [401, 403], f"Should require auth, got {response.status_code}"
            
            # Get list without auth
            response = client.get(f"{API_V1}/days/{test_day_id}/sleep", timeout=10.0)
            assert response.status_code in [401, 403], f"Should require auth, got {response.status_code}"
            
            print("\n✅ Sleep endpoints properly require authentication")
    
    def test_user_cannot_access_other_user_sleep(self, auth_headers, test_day_id):
        """Test that users can only access their own sleep records."""
        # Create a sleep record first
        now = datetime.now()
        bedtime = now.replace(hour=23, minute=0, second=0, microsecond=0) - timedelta(days=1)
        wake_time = now.replace(hour=7, minute=0, second=0, microsecond=0)
        
        with httpx.Client() as client:
            # Create sleep record with authenticated user
            create_response = client.post(
                f"{API_V1}/days/{test_day_id}/sleep",
                json={
                    "bedtime": bedtime.isoformat(),
                    "wake_time": wake_time.isoformat(),
                    "duration": 8.0,
                    "quality": 4,
                    "day_id": test_day_id
                },
                headers=auth_headers,
                timeout=10.0
            )
            
            assert create_response.status_code == 201
            sleep_id = create_response.json()["id"]
            
            # Create another user
            timestamp = str(int(datetime.now().timestamp()))
            other_user_email = f"testsleepother{timestamp}@example.com"
            other_user_username = f"testsleepother{timestamp}"
            
            register_response = client.post(
                f"{API_V1}/auth/register",
                json={
                    "email": other_user_email,
                    "username": other_user_username,
                    "password": "OtherPassword123!",
                    "full_name": "Other User"
                }
            )
            
            # Login as other user
            login_response = client.post(
                f"{API_V1}/auth/login",
                json={
                    "email": other_user_email,
                    "password": "OtherPassword123!"
                }
            )
            
            assert login_response.status_code == 200
            other_token = login_response.json()["access_token"]
            other_headers = {"Authorization": f"Bearer {other_token}"}
            
            # Try to access original user's sleep record
            access_response = client.get(
                f"{API_V1}/sleep/{sleep_id}",
                headers=other_headers,
                timeout=10.0
            )
            
            assert access_response.status_code == 403, f"Should be forbidden, got {access_response.status_code}"
            
            # Cleanup: delete the sleep record with original user
            client.delete(
                f"{API_V1}/sleep/{sleep_id}",
                headers=auth_headers,
                timeout=10.0
            )
            
            print("\n✅ Authorization properly prevents cross-user access")


# ===========================
# ERROR HANDLING TESTS
# ===========================

class TestSleepErrorHandling:
    """Test error handling for Sleep endpoints."""
    
    def test_get_nonexistent_sleep(self, auth_headers):
        """Test GET for non-existent sleep record returns 404."""
        with httpx.Client() as client:
            response = client.get(
                f"{API_V1}/sleep/999999",
                headers=auth_headers,
                timeout=10.0
            )
            
            assert response.status_code == 404, f"Should return 404, got {response.status_code}"
            
            print("\n✅ 404 error handling working correctly")
    
    def test_update_nonexistent_sleep(self, auth_headers):
        """Test UPDATE for non-existent sleep record returns 404."""
        with httpx.Client() as client:
            response = client.put(
                f"{API_V1}/sleep/999999",
                json={"quality": 5},
                headers=auth_headers,
                timeout=10.0
            )
            
            assert response.status_code == 404, f"Should return 404, got {response.status_code}"
            
            print("\n✅ 404 error handling for update working correctly")
    
    def test_delete_nonexistent_sleep(self, auth_headers):
        """Test DELETE for non-existent sleep record returns 404."""
        with httpx.Client() as client:
            response = client.delete(
                f"{API_V1}/sleep/999999",
                headers=auth_headers,
                timeout=10.0
            )
            
            assert response.status_code == 404, f"Should return 404, got {response.status_code}"
            
            print("\n✅ 404 error handling for delete working correctly")
    
    def test_create_sleep_invalid_day(self, auth_headers):
        """Test CREATE with invalid day_id returns 404."""
        now = datetime.now()
        bedtime = now.replace(hour=23, minute=0, second=0, microsecond=0) - timedelta(days=1)
        wake_time = now.replace(hour=7, minute=0, second=0, microsecond=0)
        
        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/days/999999/sleep",
                json={
                    "bedtime": bedtime.isoformat(),
                    "wake_time": wake_time.isoformat(),
                    "duration": 8.0,
                    "quality": 4,
                    "day_id": 999999
                },
                headers=auth_headers,
                timeout=10.0
            )
            
            assert response.status_code == 404, f"Should return 404, got {response.status_code}"
            
            print("\n✅ 404 error handling for invalid day_id working correctly")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
