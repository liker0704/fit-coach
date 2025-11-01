"""Integration tests for Day CRUD API endpoints."""

import httpx
import pytest
from datetime import date, timedelta
import time

# Base URL for the API
BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"

# Shared test user data - created once, reused across tests
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
    timestamp = str(int(time.time()))
    _test_user_email = f"testdaycrud{timestamp}@example.com"
    _test_user_username = f"testdaycrud{timestamp}"
    
    with httpx.Client() as client:
        # Try to register
        response = client.post(
            f"{API_V1}/auth/register",
            json={
                "email": _test_user_email,
                "username": _test_user_username,
                "password": _test_user_password,
                "full_name": "Test User Day CRUD"
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


class TestDayCRUDAPI:
    """Test suite for Day CRUD operations."""
    
    def test_01_create_day_for_today(self, auth_headers):
        """Test POST /api/v1/days - Create day for today."""
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
            
            # Verify response structure
            assert "id" in data, "Response missing 'id'"
            assert "user_id" in data, "Response missing 'user_id'"
            assert "date" in data, "Response missing 'date'"
            assert data["date"] == today, f"Expected date {today}, got {data['date']}"
            
            print(f"\n✅ Created day: ID={data['id']}, Date={data['date']}")
    
    def test_02_create_same_day_again(self, auth_headers):
        """Test POST /api/v1/days - Creating same day returns existing."""
        today = date.today().isoformat()
        
        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/days",
                json={"date": today},
                headers=auth_headers,
                timeout=10.0
            )
            
            # Should return existing day (201 status due to endpoint design)
            assert response.status_code == 201, f"Failed to get existing day: {response.text}"
            data = response.json()
            
            assert data["date"] == today
            print(f"\n✅ Got existing day: ID={data['id']}")
    
    def test_03_get_day_by_date(self, auth_headers):
        """Test GET /api/v1/days/{date} - Get specific day by date."""
        today = date.today().isoformat()
        
        with httpx.Client() as client:
            response = client.get(
                f"{API_V1}/days/{today}",
                headers=auth_headers,
                timeout=10.0
            )
            
            assert response.status_code == 200, f"Failed to get day: {response.text}"
            data = response.json()
            
            assert data["date"] == today
            assert "id" in data
            assert "user_id" in data
            print(f"\n✅ Retrieved day by date: {data['date']}")
    
    def test_04_get_nonexistent_day(self, auth_headers):
        """Test GET /api/v1/days/{date} - Getting non-existent day returns 404."""
        # Use a date far in the past that shouldn't exist
        old_date = (date.today() - timedelta(days=365)).isoformat()
        
        with httpx.Client() as client:
            response = client.get(
                f"{API_V1}/days/{old_date}",
                headers=auth_headers,
                timeout=10.0
            )
            
            assert response.status_code == 404, f"Expected 404, got {response.status_code}"
            print(f"\n✅ Correctly returned 404 for non-existent day")
    
    def test_05_get_days_without_params(self, auth_headers):
        """Test GET /api/v1/days - Get days without params (last 7 days)."""
        with httpx.Client() as client:
            response = client.get(
                f"{API_V1}/days",
                headers=auth_headers,
                timeout=10.0
            )
            
            assert response.status_code == 200, f"Failed to get days: {response.text}"
            data = response.json()
            
            assert isinstance(data, list), "Response should be a list"
            # Should contain at least the day we created
            assert len(data) >= 1, "Should return at least one day"
            print(f"\n✅ Retrieved {len(data)} days (last 7 days)")
    
    def test_06_get_days_with_date_range(self, auth_headers):
        """Test GET /api/v1/days - Get days with start_date and end_date."""
        today = date.today()
        start_date = (today - timedelta(days=7)).isoformat()
        end_date = today.isoformat()
        
        with httpx.Client() as client:
            response = client.get(
                f"{API_V1}/days",
                params={"start_date": start_date, "end_date": end_date},
                headers=auth_headers,
                timeout=10.0
            )
            
            assert response.status_code == 200, f"Failed to get days: {response.text}"
            data = response.json()
            
            assert isinstance(data, list), "Response should be a list"
            
            # Verify created day is in the list
            today_str = today.isoformat()
            day_dates = [d["date"] for d in data]
            assert today_str in day_dates, f"Today's day should be in the list"
            print(f"\n✅ Retrieved {len(data)} days in date range")
    
    def test_07_update_day(self, auth_headers):
        """Test PUT /api/v1/days/{day_id} - Update day fields."""
        today = date.today().isoformat()
        
        with httpx.Client() as client:
            # First get the day to get its ID
            get_response = client.get(
                f"{API_V1}/days/{today}",
                headers=auth_headers,
                timeout=10.0
            )
            assert get_response.status_code == 200, f"Failed to get day: {get_response.text}"
            day_data = get_response.json()
            day_id = day_data["id"]
            
            # Update the day
            update_data = {
                "tag": "workout",
                "feeling": 4,
                "effort_score": 8.5,
                "summary": "Great workout day!"
            }
            
            update_response = client.put(
                f"{API_V1}/days/{day_id}",
                json=update_data,
                headers=auth_headers,
                timeout=10.0
            )
            
            assert update_response.status_code == 200, f"Failed to update day: {update_response.text}"
            updated_data = update_response.json()
            
            # Verify updated fields
            assert updated_data["tag"] == "workout"
            assert updated_data["feeling"] == 4
            assert float(updated_data["effort_score"]) == 8.5
            assert updated_data["summary"] == "Great workout day!"
            print(f"\n✅ Updated day: tag={updated_data['tag']}, feeling={updated_data['feeling']}, effort={updated_data['effort_score']}")
    
    def test_08_update_nonexistent_day(self, auth_headers):
        """Test PUT /api/v1/days/{day_id} - Updating non-existent day returns 404."""
        nonexistent_id = 999999
        
        with httpx.Client() as client:
            response = client.put(
                f"{API_V1}/days/{nonexistent_id}",
                json={"tag": "test"},
                headers=auth_headers,
                timeout=10.0
            )
            
            assert response.status_code == 404, f"Expected 404, got {response.status_code}"
            print(f"\n✅ Correctly returned 404 for non-existent day update")
    
    def test_09_delete_day(self, auth_headers):
        """Test DELETE /api/v1/days/{day_id} - Delete day."""
        today = date.today().isoformat()
        
        with httpx.Client() as client:
            # Get the day to get its ID
            get_response = client.get(
                f"{API_V1}/days/{today}",
                headers=auth_headers,
                timeout=10.0
            )
            assert get_response.status_code == 200, f"Failed to get day: {get_response.text}"
            day_data = get_response.json()
            day_id = day_data["id"]
            
            # Delete the day
            delete_response = client.delete(
                f"{API_V1}/days/{day_id}",
                headers=auth_headers,
                timeout=10.0
            )
            
            assert delete_response.status_code == 204, f"Failed to delete day: {delete_response.text}"
            
            # Verify day is deleted - try to get it
            verify_response = client.get(
                f"{API_V1}/days/{today}",
                headers=auth_headers,
                timeout=10.0
            )
            
            assert verify_response.status_code == 404, "Day should be deleted"
            print(f"\n✅ Deleted day: ID={day_id}")
    
    def test_10_delete_nonexistent_day(self, auth_headers):
        """Test DELETE /api/v1/days/{day_id} - Deleting non-existent day returns 404."""
        nonexistent_id = 999999
        
        with httpx.Client() as client:
            response = client.delete(
                f"{API_V1}/days/{nonexistent_id}",
                headers=auth_headers,
                timeout=10.0
            )
            
            assert response.status_code == 404, f"Expected 404, got {response.status_code}"
            print(f"\n✅ Correctly returned 404 for non-existent day deletion")
    
    def test_11_unauthorized_access(self):
        """Test API endpoints without authentication - should return 401 or 403."""
        today = date.today().isoformat()
        
        with httpx.Client() as client:
            # Try to create day without auth
            response = client.post(
                f"{API_V1}/days",
                json={"date": today},
                timeout=10.0
            )
            assert response.status_code in [401, 403], f"Should require authentication, got {response.status_code}"
            
            # Try to get day without auth
            response = client.get(f"{API_V1}/days/{today}", timeout=10.0)
            assert response.status_code in [401, 403], f"Should require authentication, got {response.status_code}"
            
            # Try to get days list without auth
            response = client.get(f"{API_V1}/days", timeout=10.0)
            assert response.status_code in [401, 403], f"Should require authentication, got {response.status_code}"
            
            print(f"\n✅ All endpoints properly require authentication")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
