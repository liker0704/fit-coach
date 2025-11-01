"""Integration tests for Batch 3: Goals, Notifications, and Email Verification API endpoints."""

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
_test_user_id = None


def get_or_create_test_user():
    """Get or create test user and return credentials."""
    global _test_user_email, _test_user_username, _access_token, _test_user_id
    
    if _access_token:
        return _access_token
    
    # Create unique username/email for this test session
    timestamp = str(int(datetime.now().timestamp()))
    _test_user_email = f"testbatch3_{timestamp}@example.com"
    _test_user_username = f"testbatch3_{timestamp}"
    
    with httpx.Client() as client:
        # Register
        response = client.post(
            f"{API_V1}/auth/register",
            json={
                "email": _test_user_email,
                "username": _test_user_username,
                "password": _test_user_password,
                "full_name": "Test User Batch3"
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
        
        # Get user ID
        me_response = client.get(
            f"{API_V1}/auth/me",
            headers={"Authorization": f"Bearer {_access_token}"}
        )
        _test_user_id = me_response.json()["id"]
        
        return _access_token


@pytest.fixture
def auth_headers():
    """Get authorization headers with access token."""
    token = get_or_create_test_user()
    return {"Authorization": f"Bearer {token}"}


# ===========================
# GOALS MODULE TESTS
# ===========================

class TestGoalsCRUD:
    """Test Goals CRUD operations."""
    
    def test_create_goal_weight(self, auth_headers):
        """Test creating a weight goal."""
        today = date.today().isoformat()
        end_date = (date.today() + timedelta(days=30)).isoformat()
        
        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/goals",
                json={
                    "type": "weight",
                    "title": "Lose 10 pounds",
                    "description": "Weight loss goal for summer",
                    "target_value": 150.0,
                    "current_value": 160.0,
                    "unit": "lbs",
                    "start_date": today,
                    "end_date": end_date,
                    "status": "active"
                },
                headers=auth_headers,
                timeout=10.0
            )
            
            assert response.status_code == 201, f"Failed: {response.text}"
            data = response.json()
            
            assert data["type"] == "weight"
            assert data["title"] == "Lose 10 pounds"
            assert data["description"] == "Weight loss goal for summer"
            assert float(data["target_value"]) == 150.0
            assert float(data["current_value"]) == 160.0
            assert data["unit"] == "lbs"
            assert data["status"] == "active"
            assert "id" in data
            assert "created_at" in data
            
            # Store goal ID for later tests
            pytest.test_goal_id = data["id"]
    
    def test_create_goal_exercise(self, auth_headers):
        """Test creating an exercise goal."""
        today = date.today().isoformat()
        
        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/goals",
                json={
                    "type": "exercise",
                    "title": "Run 100 miles",
                    "target_value": 100.0,
                    "current_value": 0.0,
                    "unit": "miles",
                    "start_date": today
                },
                headers=auth_headers,
                timeout=10.0
            )
            
            assert response.status_code == 201, f"Failed: {response.text}"
            data = response.json()
            assert data["type"] == "exercise"
            assert data["title"] == "Run 100 miles"
    
    def test_create_goal_water(self, auth_headers):
        """Test creating a water goal."""
        today = date.today().isoformat()
        
        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/goals",
                json={
                    "type": "water",
                    "title": "Drink 8 glasses daily",
                    "target_value": 64.0,
                    "unit": "oz",
                    "start_date": today
                },
                headers=auth_headers,
                timeout=10.0
            )
            
            assert response.status_code == 201, f"Failed: {response.text}"
            data = response.json()
            assert data["type"] == "water"
    
    def test_create_goal_sleep(self, auth_headers):
        """Test creating a sleep goal."""
        today = date.today().isoformat()
        
        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/goals",
                json={
                    "type": "sleep",
                    "title": "Sleep 8 hours nightly",
                    "target_value": 8.0,
                    "unit": "hours",
                    "start_date": today
                },
                headers=auth_headers,
                timeout=10.0
            )
            
            assert response.status_code == 201, f"Failed: {response.text}"
            data = response.json()
            assert data["type"] == "sleep"
    
    def test_create_goal_calories(self, auth_headers):
        """Test creating a calories goal."""
        today = date.today().isoformat()
        
        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/goals",
                json={
                    "type": "calories",
                    "title": "Daily calorie target",
                    "target_value": 2000.0,
                    "unit": "kcal",
                    "start_date": today
                },
                headers=auth_headers,
                timeout=10.0
            )
            
            assert response.status_code == 201, f"Failed: {response.text}"
            data = response.json()
            assert data["type"] == "calories"
    
    def test_create_goal_validation_negative_target(self, auth_headers):
        """Test validation: target_value cannot be negative."""
        today = date.today().isoformat()
        
        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/goals",
                json={
                    "type": "weight",
                    "title": "Invalid goal",
                    "target_value": -10.0,
                    "start_date": today
                },
                headers=auth_headers,
                timeout=10.0
            )
            
            assert response.status_code == 422, f"Should reject negative target_value"
    
    def test_create_goal_validation_end_before_start(self, auth_headers):
        """Test validation: end_date cannot be before start_date."""
        today = date.today().isoformat()
        past_date = (date.today() - timedelta(days=10)).isoformat()
        
        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/goals",
                json={
                    "type": "weight",
                    "title": "Invalid date goal",
                    "target_value": 150.0,
                    "start_date": today,
                    "end_date": past_date
                },
                headers=auth_headers,
                timeout=10.0
            )
            
            assert response.status_code == 422, f"Should reject end_date before start_date"
    
    def test_get_all_goals(self, auth_headers):
        """Test getting all user goals."""
        with httpx.Client() as client:
            response = client.get(
                f"{API_V1}/goals",
                headers=auth_headers,
                timeout=10.0
            )
            
            assert response.status_code == 200, f"Failed: {response.text}"
            data = response.json()
            
            assert isinstance(data, list)
            assert len(data) >= 5, "Should have at least 5 goals created"
            
            # Check all goals have required fields
            for goal in data:
                assert "id" in goal
                assert "type" in goal
                assert "title" in goal
                assert "target_value" in goal
                assert "status" in goal
                assert "created_at" in goal
    
    def test_get_goals_filter_by_active_status(self, auth_headers):
        """Test filtering goals by active status."""
        with httpx.Client() as client:
            response = client.get(
                f"{API_V1}/goals?status=active",
                headers=auth_headers,
                timeout=10.0
            )
            
            assert response.status_code == 200, f"Failed: {response.text}"
            data = response.json()
            
            assert isinstance(data, list)
            # All returned goals should be active
            for goal in data:
                assert goal["status"] == "active"
    
    def test_get_goals_filter_by_completed_status(self, auth_headers):
        """Test filtering goals by completed status."""
        with httpx.Client() as client:
            response = client.get(
                f"{API_V1}/goals?status=completed",
                headers=auth_headers,
                timeout=10.0
            )
            
            assert response.status_code == 200, f"Failed: {response.text}"
            data = response.json()
            
            assert isinstance(data, list)
            # All returned goals should be completed
            for goal in data:
                assert goal["status"] == "completed"
    
    def test_get_goals_invalid_status_filter(self, auth_headers):
        """Test invalid status filter returns 400."""
        with httpx.Client() as client:
            response = client.get(
                f"{API_V1}/goals?status=invalid_status",
                headers=auth_headers,
                timeout=10.0
            )
            
            assert response.status_code == 400, f"Should reject invalid status"
    
    def test_get_specific_goal(self, auth_headers):
        """Test getting specific goal by ID."""
        # Use goal ID from create test
        if not hasattr(pytest, 'test_goal_id'):
            pytest.skip("No goal ID available")
        
        with httpx.Client() as client:
            response = client.get(
                f"{API_V1}/goals/{pytest.test_goal_id}",
                headers=auth_headers,
                timeout=10.0
            )
            
            assert response.status_code == 200, f"Failed: {response.text}"
            data = response.json()
            
            assert data["id"] == pytest.test_goal_id
            assert "title" in data
            assert "type" in data
            assert "target_value" in data
    
    def test_get_nonexistent_goal(self, auth_headers):
        """Test getting nonexistent goal returns 404."""
        with httpx.Client() as client:
            response = client.get(
                f"{API_V1}/goals/999999",
                headers=auth_headers,
                timeout=10.0
            )
            
            assert response.status_code == 404
    
    def test_update_goal_progress(self, auth_headers):
        """Test updating goal progress (current_value)."""
        if not hasattr(pytest, 'test_goal_id'):
            pytest.skip("No goal ID available")
        
        with httpx.Client() as client:
            response = client.put(
                f"{API_V1}/goals/{pytest.test_goal_id}",
                json={
                    "current_value": 155.0
                },
                headers=auth_headers,
                timeout=10.0
            )
            
            assert response.status_code == 200, f"Failed: {response.text}"
            data = response.json()
            
            assert float(data["current_value"]) == 155.0
            assert "updated_at" in data
    
    def test_update_goal_status_to_completed(self, auth_headers):
        """Test updating goal status to completed sets completed_at timestamp."""
        if not hasattr(pytest, 'test_goal_id'):
            pytest.skip("No goal ID available")
        
        with httpx.Client() as client:
            response = client.put(
                f"{API_V1}/goals/{pytest.test_goal_id}",
                json={
                    "status": "completed"
                },
                headers=auth_headers,
                timeout=10.0
            )
            
            assert response.status_code == 200, f"Failed: {response.text}"
            data = response.json()
            
            assert data["status"] == "completed"
            assert data["completed_at"] is not None, "completed_at should be set"
    
    def test_update_goal_title(self, auth_headers):
        """Test updating goal title."""
        if not hasattr(pytest, 'test_goal_id'):
            pytest.skip("No goal ID available")
        
        with httpx.Client() as client:
            response = client.put(
                f"{API_V1}/goals/{pytest.test_goal_id}",
                json={
                    "title": "Updated Goal Title"
                },
                headers=auth_headers,
                timeout=10.0
            )
            
            assert response.status_code == 200, f"Failed: {response.text}"
            data = response.json()
            
            assert data["title"] == "Updated Goal Title"
    
    def test_update_nonexistent_goal(self, auth_headers):
        """Test updating nonexistent goal returns 404."""
        with httpx.Client() as client:
            response = client.put(
                f"{API_V1}/goals/999999",
                json={
                    "title": "Updated"
                },
                headers=auth_headers,
                timeout=10.0
            )
            
            assert response.status_code == 404
    
    def test_delete_goal(self, auth_headers):
        """Test deleting a goal."""
        # Create a goal to delete
        today = date.today().isoformat()
        
        with httpx.Client() as client:
            # Create goal
            create_response = client.post(
                f"{API_V1}/goals",
                json={
                    "type": "weight",
                    "title": "Goal to delete",
                    "target_value": 150.0,
                    "start_date": today
                },
                headers=auth_headers,
                timeout=10.0
            )
            
            goal_id = create_response.json()["id"]
            
            # Delete goal
            delete_response = client.delete(
                f"{API_V1}/goals/{goal_id}",
                headers=auth_headers,
                timeout=10.0
            )
            
            assert delete_response.status_code == 204, f"Failed: {delete_response.text}"
            
            # Verify goal is deleted
            get_response = client.get(
                f"{API_V1}/goals/{goal_id}",
                headers=auth_headers,
                timeout=10.0
            )
            
            assert get_response.status_code == 404, "Goal should be deleted"
    
    def test_delete_nonexistent_goal(self, auth_headers):
        """Test deleting nonexistent goal returns 404."""
        with httpx.Client() as client:
            response = client.delete(
                f"{API_V1}/goals/999999",
                headers=auth_headers,
                timeout=10.0
            )
            
            assert response.status_code == 404


# ===========================
# NOTIFICATIONS MODULE TESTS
# ===========================

class TestNotificationsCRUD:
    """Test Notifications CRUD operations."""
    
    def test_create_notification_via_service(self, auth_headers):
        """Test creating a notification via service (no POST endpoint)."""
        # We need to create notifications directly via service for testing
        # since there's no POST endpoint for notifications
        from app.core.database import SessionLocal
        from app.services.notification_service import NotificationService
        
        db = SessionLocal()
        try:
            notification = NotificationService.create_notification(
                db,
                _test_user_id,
                {
                    "type": "goal_completed",
                    "title": "Goal Completed!",
                    "message": "You've reached your weight goal!",
                    "is_read": False
                }
            )
            
            assert notification.id is not None
            pytest.test_notification_id = notification.id
        finally:
            db.close()
    
    def test_get_all_notifications(self, auth_headers):
        """Test getting all user notifications."""
        with httpx.Client() as client:
            response = client.get(
                f"{API_V1}/notifications",
                headers=auth_headers,
                timeout=10.0
            )
            
            assert response.status_code == 200, f"Failed: {response.text}"
            data = response.json()
            
            assert isinstance(data, list)
            
            # Check notifications have required fields
            for notification in data:
                assert "id" in notification
                assert "type" in notification
                assert "title" in notification
                assert "is_read" in notification
                assert "created_at" in notification
    
    def test_get_notifications_unread_only(self, auth_headers):
        """Test filtering to show only unread notifications."""
        with httpx.Client() as client:
            response = client.get(
                f"{API_V1}/notifications?unread_only=true",
                headers=auth_headers,
                timeout=10.0
            )
            
            assert response.status_code == 200, f"Failed: {response.text}"
            data = response.json()
            
            assert isinstance(data, list)
            # All returned notifications should be unread
            for notification in data:
                assert notification["is_read"] == False
    
    def test_get_specific_notification(self, auth_headers):
        """Test getting specific notification by ID."""
        if not hasattr(pytest, 'test_notification_id'):
            pytest.skip("No notification ID available")
        
        with httpx.Client() as client:
            response = client.get(
                f"{API_V1}/notifications/{pytest.test_notification_id}",
                headers=auth_headers,
                timeout=10.0
            )
            
            assert response.status_code == 200, f"Failed: {response.text}"
            data = response.json()
            
            assert data["id"] == pytest.test_notification_id
            assert "title" in data
            assert "type" in data
    
    def test_get_nonexistent_notification(self, auth_headers):
        """Test getting nonexistent notification returns 404."""
        with httpx.Client() as client:
            response = client.get(
                f"{API_V1}/notifications/999999",
                headers=auth_headers,
                timeout=10.0
            )
            
            assert response.status_code == 404
    
    def test_mark_notification_as_read(self, auth_headers):
        """Test marking notification as read."""
        if not hasattr(pytest, 'test_notification_id'):
            pytest.skip("No notification ID available")
        
        with httpx.Client() as client:
            response = client.put(
                f"{API_V1}/notifications/{pytest.test_notification_id}/read",
                headers=auth_headers,
                timeout=10.0
            )
            
            assert response.status_code == 200, f"Failed: {response.text}"
            data = response.json()
            
            assert data["is_read"] == True
            assert data["read_at"] is not None, "read_at timestamp should be set"
    
    def test_mark_nonexistent_notification_as_read(self, auth_headers):
        """Test marking nonexistent notification as read returns 404."""
        with httpx.Client() as client:
            response = client.put(
                f"{API_V1}/notifications/999999/read",
                headers=auth_headers,
                timeout=10.0
            )
            
            assert response.status_code == 404
    
    def test_delete_notification(self, auth_headers):
        """Test deleting a notification."""
        # Create a notification to delete
        from app.core.database import SessionLocal
        from app.services.notification_service import NotificationService
        
        db = SessionLocal()
        try:
            notification = NotificationService.create_notification(
                db,
                _test_user_id,
                {
                    "type": "reminder",
                    "title": "Notification to delete",
                    "message": "This will be deleted"
                }
            )
            notification_id = notification.id
        finally:
            db.close()
        
        with httpx.Client() as client:
            # Delete notification
            delete_response = client.delete(
                f"{API_V1}/notifications/{notification_id}",
                headers=auth_headers,
                timeout=10.0
            )
            
            assert delete_response.status_code == 204, f"Failed: {delete_response.text}"
            
            # Verify notification is deleted
            get_response = client.get(
                f"{API_V1}/notifications/{notification_id}",
                headers=auth_headers,
                timeout=10.0
            )
            
            assert get_response.status_code == 404, "Notification should be deleted"
    
    def test_delete_nonexistent_notification(self, auth_headers):
        """Test deleting nonexistent notification returns 404."""
        with httpx.Client() as client:
            response = client.delete(
                f"{API_V1}/notifications/999999",
                headers=auth_headers,
                timeout=10.0
            )
            
            assert response.status_code == 404


# ===========================
# EMAIL VERIFICATION TESTS
# ===========================

class TestEmailVerification:
    """Test Email Verification functionality."""
    
    def test_register_new_user_unverified(self):
        """Test that newly registered users are unverified by default."""
        timestamp = str(int(datetime.now().timestamp()))
        email = f"verification_test_{timestamp}@example.com"
        username = f"verifytest_{timestamp}"
        
        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/auth/register",
                json={
                    "email": email,
                    "username": username,
                    "password": "TestPassword123!",
                    "full_name": "Verification Test User"
                }
            )
            
            assert response.status_code == 201, f"Registration failed: {response.text}"
            data = response.json()
            
            # User should be created but not verified
            assert data["is_verified"] == False
            
            # Store for later tests
            pytest.verify_email = email
            pytest.verify_password = "TestPassword123!"
    
    def test_resend_verification_for_unverified_user(self):
        """Test resending verification token to unverified user."""
        if not hasattr(pytest, 'verify_email'):
            pytest.skip("No verification email available")
        
        with httpx.Client() as client:
            # Login first
            login_response = client.post(
                f"{API_V1}/auth/login",
                json={
                    "email": pytest.verify_email,
                    "password": pytest.verify_password
                }
            )
            
            token = login_response.json()["access_token"]
            
            # Resend verification
            response = client.post(
                f"{API_V1}/auth/resend-verification",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10.0
            )
            
            assert response.status_code == 200, f"Failed: {response.text}"
            data = response.json()
            
            assert "message" in data
            assert "token" in data, "Token should be returned in MVP"
            
            # Store token for verification test
            pytest.verification_token = data["token"]
    
    def test_verify_email_with_valid_token(self):
        """Test verifying email with valid token."""
        if not hasattr(pytest, 'verification_token'):
            pytest.skip("No verification token available")
        
        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/auth/verify-email",
                json={
                    "token": pytest.verification_token
                },
                timeout=10.0
            )
            
            assert response.status_code == 200, f"Failed: {response.text}"
            data = response.json()
            
            assert data["message"] == "Email verified successfully"
    
    def test_verify_email_with_invalid_token(self):
        """Test verifying email with invalid token returns 400."""
        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/auth/verify-email",
                json={
                    "token": "invalid_token_12345"
                },
                timeout=10.0
            )
            
            assert response.status_code == 400
    
    def test_verify_email_with_used_token(self):
        """Test that verification token is single-use."""
        if not hasattr(pytest, 'verification_token'):
            pytest.skip("No verification token available")
        
        with httpx.Client() as client:
            response = client.post(
                f"{API_V1}/auth/verify-email",
                json={
                    "token": pytest.verification_token
                },
                timeout=10.0
            )
            
            # Should fail since token was already used
            assert response.status_code == 400
    
    def test_resend_verification_already_verified(self):
        """Test that verified users cannot resend verification."""
        if not hasattr(pytest, 'verify_email'):
            pytest.skip("No verification email available")
        
        with httpx.Client() as client:
            # Login
            login_response = client.post(
                f"{API_V1}/auth/login",
                json={
                    "email": pytest.verify_email,
                    "password": pytest.verify_password
                }
            )
            
            token = login_response.json()["access_token"]
            
            # Try to resend (should fail since already verified)
            response = client.post(
                f"{API_V1}/auth/resend-verification",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10.0
            )
            
            assert response.status_code == 400, "Already verified users should not be able to resend"


# ===========================
# AUTHORIZATION TESTS
# ===========================

class TestAuthorization:
    """Test that users can only access their own resources."""
    
    def test_cannot_access_other_user_goal(self, auth_headers):
        """Test that users cannot access other users' goals."""
        # Create a second user
        timestamp = str(int(datetime.now().timestamp()))
        email2 = f"otheruser_{timestamp}@example.com"
        username2 = f"otheruser_{timestamp}"
        
        with httpx.Client() as client:
            # Register second user
            client.post(
                f"{API_V1}/auth/register",
                json={
                    "email": email2,
                    "username": username2,
                    "password": "TestPassword123!",
                    "full_name": "Other User"
                }
            )
            
            # Login as second user
            login_response = client.post(
                f"{API_V1}/auth/login",
                json={
                    "email": email2,
                    "password": "TestPassword123!"
                }
            )
            
            token2 = login_response.json()["access_token"]
            headers2 = {"Authorization": f"Bearer {token2}"}
            
            # Try to access first user's goal
            if hasattr(pytest, 'test_goal_id'):
                response = client.get(
                    f"{API_V1}/goals/{pytest.test_goal_id}",
                    headers=headers2,
                    timeout=10.0
                )
                
                assert response.status_code == 403, "Should not access other user's goal"
    
    def test_cannot_access_other_user_notification(self, auth_headers):
        """Test that users cannot access other users' notifications."""
        # Create a second user
        timestamp = str(int(datetime.now().timestamp()))
        email2 = f"otheruser2_{timestamp}@example.com"
        username2 = f"otheruser2_{timestamp}"
        
        with httpx.Client() as client:
            # Register second user
            client.post(
                f"{API_V1}/auth/register",
                json={
                    "email": email2,
                    "username": username2,
                    "password": "TestPassword123!",
                    "full_name": "Other User 2"
                }
            )
            
            # Login as second user
            login_response = client.post(
                f"{API_V1}/auth/login",
                json={
                    "email": email2,
                    "password": "TestPassword123!"
                }
            )
            
            token2 = login_response.json()["access_token"]
            headers2 = {"Authorization": f"Bearer {token2}"}
            
            # Try to access first user's notification
            if hasattr(pytest, 'test_notification_id'):
                response = client.get(
                    f"{API_V1}/notifications/{pytest.test_notification_id}",
                    headers=headers2,
                    timeout=10.0
                )
                
                assert response.status_code == 403, "Should not access other user's notification"
