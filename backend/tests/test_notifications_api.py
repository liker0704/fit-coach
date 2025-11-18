"""Integration tests for Notifications API endpoints."""

import httpx
import pytest
from datetime import datetime
from unittest.mock import patch
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
    _test_user_email = f"testnotif{timestamp}@example.com"
    _test_user_username = f"testnotif{timestamp}"

    with httpx.Client() as client:
        # Register
        response = client.post(
            f"{API_V1}/auth/register",
            json={
                "email": _test_user_email,
                "username": _test_user_username,
                "password": _test_user_password,
                "full_name": "Test Notification User"
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


def create_test_notification(notification_data=None):
    """Create a test notification using internal service."""
    if notification_data is None:
        notification_data = {
            "type": "info",
            "title": "Test Notification",
            "message": "This is a test notification",
            "data": {"key": "value"}
        }

    # Direct database insertion for testing
    # In real scenario, notifications are created by the system, not users
    from app.core.database import get_db
    from app.services.notification_service import NotificationService
    from app.models.user import User

    db_gen = get_db()
    db = next(db_gen)

    try:
        # Get user by email
        user = db.query(User).filter(User.email == _test_user_email).first()
        if user:
            notification = NotificationService.create_notification(
                db, user.id, notification_data
            )
            return notification.id
    finally:
        db_gen.close()

    return None


class TestNotificationsCRUD:
    """Test suite for Notification CRUD operations."""

    notification_id = None

    def test_01_get_notifications_empty(self):
        """Test GET /api/v1/notifications - Empty list initially."""
        with httpx.Client() as client:
            response = client.get(
                f"{API_V1}/notifications",
                headers=get_auth_headers(),
                timeout=10.0
            )

            assert response.status_code == 200, f"Failed to get notifications: {response.text}"
            data = response.json()

            assert isinstance(data, list), "Response should be a list"
            print(f"\nInitial notifications count: {len(data)}")

    def test_02_create_notification_via_service(self):
        """Test creating notification via service (notifications are system-generated)."""
        notification_data = {
            "type": "achievement",
            "title": "First Workout Complete!",
            "message": "Congratulations on completing your first workout",
            "data": {"workout_id": 123, "points": 50}
        }

        notification_id = create_test_notification(notification_data)
        assert notification_id is not None, "Failed to create notification"

        TestNotificationsCRUD.notification_id = notification_id
        print(f"\nCreated notification: ID={notification_id}")

    def test_03_get_notifications_list(self):
        """Test GET /api/v1/notifications - Get all notifications."""
        with httpx.Client() as client:
            response = client.get(
                f"{API_V1}/notifications",
                headers=get_auth_headers(),
                timeout=10.0
            )

            assert response.status_code == 200, f"Failed to get notifications: {response.text}"
            data = response.json()

            assert isinstance(data, list), "Response should be a list"
            assert len(data) >= 1, "Should have at least one notification"

            # Verify structure
            first_notif = data[0]
            assert "id" in first_notif
            assert "type" in first_notif
            assert "title" in first_notif
            assert "message" in first_notif
            assert "is_read" in first_notif
            assert "created_at" in first_notif

            print(f"\nRetrieved {len(data)} notifications")

    def test_04_get_unread_notifications(self):
        """Test GET /api/v1/notifications?unread_only=true - Get only unread."""
        with httpx.Client() as client:
            response = client.get(
                f"{API_V1}/notifications?unread_only=true",
                headers=get_auth_headers(),
                timeout=10.0
            )

            assert response.status_code == 200, f"Failed to get unread notifications: {response.text}"
            data = response.json()

            assert isinstance(data, list), "Response should be a list"

            # All notifications should be unread
            for notif in data:
                assert notif["is_read"] is False, "All notifications should be unread"

            print(f"\nUnread notifications: {len(data)}")

    def test_05_get_notification_by_id(self):
        """Test GET /api/v1/notifications/{id} - Get specific notification."""
        assert TestNotificationsCRUD.notification_id is not None, "No notification ID available"

        with httpx.Client() as client:
            response = client.get(
                f"{API_V1}/notifications/{TestNotificationsCRUD.notification_id}",
                headers=get_auth_headers(),
                timeout=10.0
            )

            assert response.status_code == 200, f"Failed to get notification: {response.text}"
            data = response.json()

            assert data["id"] == TestNotificationsCRUD.notification_id
            assert data["type"] == "achievement"
            assert data["title"] == "First Workout Complete!"
            assert data["is_read"] is False

            print(f"\nRetrieved notification: ID={data['id']}, Title={data['title']}")

    def test_06_get_nonexistent_notification(self):
        """Test GET /api/v1/notifications/{id} - 404 for non-existent notification."""
        with httpx.Client() as client:
            response = client.get(
                f"{API_V1}/notifications/999999",
                headers=get_auth_headers(),
                timeout=10.0
            )

            assert response.status_code == 404, "Should return 404 for non-existent notification"
            print("\nCorrectly returned 404 for non-existent notification")

    def test_07_mark_notification_as_read(self):
        """Test PUT /api/v1/notifications/{id}/read - Mark as read."""
        assert TestNotificationsCRUD.notification_id is not None, "No notification ID available"

        with httpx.Client() as client:
            response = client.put(
                f"{API_V1}/notifications/{TestNotificationsCRUD.notification_id}/read",
                headers=get_auth_headers(),
                timeout=10.0
            )

            assert response.status_code == 200, f"Failed to mark as read: {response.text}"
            data = response.json()

            assert data["is_read"] is True, "Notification should be marked as read"
            assert data["read_at"] is not None, "read_at should be set"

            print(f"\nMarked notification as read: ID={data['id']}")

    def test_08_mark_already_read_notification(self):
        """Test marking already-read notification (should succeed)."""
        assert TestNotificationsCRUD.notification_id is not None, "No notification ID available"

        with httpx.Client() as client:
            response = client.put(
                f"{API_V1}/notifications/{TestNotificationsCRUD.notification_id}/read",
                headers=get_auth_headers(),
                timeout=10.0
            )

            assert response.status_code == 200, "Should succeed even if already read"
            data = response.json()
            assert data["is_read"] is True

            print("\nSuccessfully handled already-read notification")

    def test_09_get_unread_after_marking(self):
        """Test that unread_only filter works after marking as read."""
        with httpx.Client() as client:
            response = client.get(
                f"{API_V1}/notifications?unread_only=true",
                headers=get_auth_headers(),
                timeout=10.0
            )

            assert response.status_code == 200
            data = response.json()

            # Our marked notification should not be in unread list
            notification_ids = [n["id"] for n in data]
            assert TestNotificationsCRUD.notification_id not in notification_ids, \
                "Read notification should not appear in unread list"

            print(f"\nUnread filter correctly excludes read notification")

    def test_10_delete_notification(self):
        """Test DELETE /api/v1/notifications/{id} - Delete notification."""
        assert TestNotificationsCRUD.notification_id is not None, "No notification ID available"

        with httpx.Client() as client:
            response = client.delete(
                f"{API_V1}/notifications/{TestNotificationsCRUD.notification_id}",
                headers=get_auth_headers(),
                timeout=10.0
            )

            assert response.status_code == 204, f"Failed to delete notification: {response.text}"

            # Verify deletion
            verify_response = client.get(
                f"{API_V1}/notifications/{TestNotificationsCRUD.notification_id}",
                headers=get_auth_headers(),
                timeout=10.0
            )

            assert verify_response.status_code == 404, "Notification should be deleted"

            print(f"\nDeleted notification: ID={TestNotificationsCRUD.notification_id}")

    def test_11_delete_nonexistent_notification(self):
        """Test DELETE /api/v1/notifications/{id} - 404 for non-existent."""
        with httpx.Client() as client:
            response = client.delete(
                f"{API_V1}/notifications/999999",
                headers=get_auth_headers(),
                timeout=10.0
            )

            assert response.status_code == 404, "Should return 404 for non-existent notification"
            print("\nCorrectly returned 404 when deleting non-existent notification")


class TestNotificationTypes:
    """Test different notification types."""

    def test_create_various_notification_types(self):
        """Test creating notifications with different types."""
        notification_types = [
            {
                "type": "info",
                "title": "Info Notification",
                "message": "This is an informational message"
            },
            {
                "type": "warning",
                "title": "Warning Notification",
                "message": "This is a warning message"
            },
            {
                "type": "achievement",
                "title": "Achievement Unlocked",
                "message": "You've reached a milestone!",
                "data": {"achievement_id": 42, "points": 100}
            },
            {
                "type": "reminder",
                "title": "Workout Reminder",
                "message": "Time for your daily workout",
                "data": {"workout_type": "cardio", "scheduled_time": "18:00"}
            },
            {
                "type": "social",
                "title": "New Follower",
                "message": "John Doe started following you",
                "data": {"user_id": 123, "username": "johndoe"}
            }
        ]

        notification_ids = []
        for notif_data in notification_types:
            notif_id = create_test_notification(notif_data)
            assert notif_id is not None, f"Failed to create {notif_data['type']} notification"
            notification_ids.append(notif_id)

        print(f"\nCreated {len(notification_ids)} notifications of different types")

        # Verify all notifications are retrieved
        with httpx.Client() as client:
            response = client.get(
                f"{API_V1}/notifications",
                headers=get_auth_headers(),
                timeout=10.0
            )

            assert response.status_code == 200
            data = response.json()

            # Check that we have at least the notifications we created
            assert len(data) >= len(notification_types), "Should retrieve all created notifications"

            # Verify types are preserved
            types_in_response = {n["type"] for n in data}
            expected_types = {n["type"] for n in notification_types}
            assert expected_types.issubset(types_in_response), "All notification types should be present"

            print(f"Verified notification types: {sorted(types_in_response)}")


class TestNotificationAuthorization:
    """Test authorization and access control for notifications."""

    def test_notifications_require_auth(self):
        """Test that notification endpoints require authentication."""
        with httpx.Client() as client:
            # GET list without auth
            response = client.get(f"{API_V1}/notifications", timeout=10.0)
            assert response.status_code in [401, 403], "Should require authentication"

            # GET specific without auth
            response = client.get(f"{API_V1}/notifications/1", timeout=10.0)
            assert response.status_code in [401, 403], "Should require authentication"

            # PUT without auth
            response = client.put(f"{API_V1}/notifications/1/read", timeout=10.0)
            assert response.status_code in [401, 403], "Should require authentication"

            # DELETE without auth
            response = client.delete(f"{API_V1}/notifications/1", timeout=10.0)
            assert response.status_code in [401, 403], "Should require authentication"

            print("\nAll notification endpoints correctly require authentication")

    def test_cannot_access_other_users_notification(self):
        """Test that users cannot access other users' notifications."""
        # Create notification for current user
        notification_id = create_test_notification({
            "type": "test",
            "title": "Test Notification",
            "message": "For authorization test"
        })

        # Create second user
        timestamp = str(int(datetime.now().timestamp()))
        second_user_email = f"testnotif2_{timestamp}@example.com"
        second_user_username = f"testnotif2_{timestamp}"
        second_user_password = "TestPassword123!"

        with httpx.Client() as client:
            # Register second user
            client.post(
                f"{API_V1}/auth/register",
                json={
                    "email": second_user_email,
                    "username": second_user_username,
                    "password": second_user_password,
                    "full_name": "Second Test User"
                }
            )

            # Login as second user
            login_response = client.post(
                f"{API_V1}/auth/login",
                json={
                    "email": second_user_email,
                    "password": second_user_password
                }
            )

            second_user_token = login_response.json()["access_token"]
            second_user_headers = {"Authorization": f"Bearer {second_user_token}"}

            # Try to access first user's notification
            response = client.get(
                f"{API_V1}/notifications/{notification_id}",
                headers=second_user_headers,
                timeout=10.0
            )

            assert response.status_code == 403, "Should not be able to access other user's notification"

            # Try to mark as read
            response = client.put(
                f"{API_V1}/notifications/{notification_id}/read",
                headers=second_user_headers,
                timeout=10.0
            )

            assert response.status_code == 403, "Should not be able to update other user's notification"

            # Try to delete
            response = client.delete(
                f"{API_V1}/notifications/{notification_id}",
                headers=second_user_headers,
                timeout=10.0
            )

            assert response.status_code == 403, "Should not be able to delete other user's notification"

            print("\nCorrectly prevented access to other user's notifications")


class TestNotificationDataFields:
    """Test notification data field functionality."""

    def test_notification_with_json_data(self):
        """Test notification with complex JSON data field."""
        complex_data = {
            "workout": {
                "id": 456,
                "type": "strength",
                "exercises": ["bench press", "squats", "deadlifts"]
            },
            "stats": {
                "duration": 3600,
                "calories": 450,
                "sets_completed": 12
            },
            "achievements": ["personal_best", "consistency_streak"]
        }

        notification_id = create_test_notification({
            "type": "workout_summary",
            "title": "Workout Complete",
            "message": "Great job on your strength training!",
            "data": complex_data
        })

        assert notification_id is not None, "Failed to create notification with complex data"

        # Retrieve and verify data structure
        with httpx.Client() as client:
            response = client.get(
                f"{API_V1}/notifications/{notification_id}",
                headers=get_auth_headers(),
                timeout=10.0
            )

            assert response.status_code == 200
            data = response.json()

            # Verify data field is preserved correctly
            assert data["data"] is not None
            assert data["data"]["workout"]["id"] == 456
            assert data["data"]["stats"]["calories"] == 450
            assert "personal_best" in data["data"]["achievements"]

            print("\nComplex JSON data correctly stored and retrieved")

    def test_notification_without_data(self):
        """Test notification without data field (optional)."""
        notification_id = create_test_notification({
            "type": "simple",
            "title": "Simple Notification",
            "message": "No additional data"
        })

        assert notification_id is not None

        with httpx.Client() as client:
            response = client.get(
                f"{API_V1}/notifications/{notification_id}",
                headers=get_auth_headers(),
                timeout=10.0
            )

            assert response.status_code == 200
            data = response.json()
            # data field should be None or not present
            assert data.get("data") is None or "data" not in data

            print("\nNotification without data field works correctly")


class TestNotificationPagination:
    """Test notification list ordering and pagination."""

    def test_notifications_ordered_by_date(self):
        """Test that notifications are ordered by created_at DESC."""
        # Create multiple notifications with slight delays
        import time

        notification_ids = []
        for i in range(3):
            notif_id = create_test_notification({
                "type": "test",
                "title": f"Test Notification {i+1}",
                "message": f"Message {i+1}"
            })
            notification_ids.append(notif_id)
            time.sleep(0.1)  # Small delay to ensure different timestamps

        # Retrieve all notifications
        with httpx.Client() as client:
            response = client.get(
                f"{API_V1}/notifications",
                headers=get_auth_headers(),
                timeout=10.0
            )

            assert response.status_code == 200
            data = response.json()

            # Verify ordering (newest first)
            if len(data) >= 2:
                for i in range(len(data) - 1):
                    current_date = datetime.fromisoformat(data[i]["created_at"].replace('Z', '+00:00'))
                    next_date = datetime.fromisoformat(data[i+1]["created_at"].replace('Z', '+00:00'))
                    assert current_date >= next_date, "Notifications should be ordered by created_at DESC"

            print(f"\nNotifications correctly ordered by date (newest first)")


class TestNotificationEdgeCases:
    """Test edge cases and error handling."""

    def test_mark_nonexistent_notification_as_read(self):
        """Test marking non-existent notification as read."""
        with httpx.Client() as client:
            response = client.put(
                f"{API_V1}/notifications/999999/read",
                headers=get_auth_headers(),
                timeout=10.0
            )

            assert response.status_code == 404, "Should return 404 for non-existent notification"
            print("\nCorrectly handled marking non-existent notification as read")

    def test_notification_with_very_long_message(self):
        """Test notification with long message."""
        long_message = "A" * 5000  # 5000 character message

        notification_id = create_test_notification({
            "type": "test",
            "title": "Long Message Test",
            "message": long_message
        })

        assert notification_id is not None

        with httpx.Client() as client:
            response = client.get(
                f"{API_V1}/notifications/{notification_id}",
                headers=get_auth_headers(),
                timeout=10.0
            )

            assert response.status_code == 200
            data = response.json()
            assert len(data["message"]) == 5000

            print("\nLong message notification handled correctly")

    def test_notification_with_empty_message(self):
        """Test notification with empty message (should be allowed)."""
        notification_id = create_test_notification({
            "type": "test",
            "title": "Empty Message Test",
            "message": ""
        })

        assert notification_id is not None

        with httpx.Client() as client:
            response = client.get(
                f"{API_V1}/notifications/{notification_id}",
                headers=get_auth_headers(),
                timeout=10.0
            )

            assert response.status_code == 200
            data = response.json()
            assert data["message"] == ""

            print("\nEmpty message notification handled correctly")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
