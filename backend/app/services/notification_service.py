"""Notification service."""

from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.notification import Notification


class NotificationService:
    """Service for notification operations."""

    @staticmethod
    def create_notification(db: Session, user_id: int, notification_data: dict) -> Notification:
        """Create new notification for a user.

        Args:
            db: Database session
            user_id: User ID to associate notification with
            notification_data: Dictionary containing notification fields

        Returns:
            Newly created Notification object

        Raises:
            ValueError: If required fields are missing
        """
        if "type" not in notification_data:
            raise ValueError("Notification type is required")
        if "title" not in notification_data:
            raise ValueError("Notification title is required")

        new_notification = Notification(user_id=user_id, **notification_data)
        db.add(new_notification)
        db.commit()
        db.refresh(new_notification)
        return new_notification

    @staticmethod
    def get_notification(db: Session, notification_id: int) -> Optional[Notification]:
        """Get notification by ID.

        Args:
            db: Database session
            notification_id: Notification ID

        Returns:
            Notification object or None if not found
        """
        return db.query(Notification).filter(Notification.id == notification_id).first()

    @staticmethod
    def get_user_notifications(
        db: Session, user_id: int, unread_only: bool = False
    ) -> List[Notification]:
        """Get all notifications for a specific user.

        Args:
            db: Database session
            user_id: User ID
            unread_only: If True, only return unread notifications

        Returns:
            List of Notification objects ordered by created_at desc
        """
        query = db.query(Notification).filter(Notification.user_id == user_id)

        if unread_only:
            query = query.filter(Notification.is_read == False)

        return query.order_by(Notification.created_at.desc()).all()

    @staticmethod
    def mark_as_read(db: Session, notification_id: int) -> Notification:
        """Mark notification as read.

        Args:
            db: Database session
            notification_id: Notification ID

        Returns:
            Updated Notification object

        Raises:
            ValueError: If notification not found
        """
        notification = db.query(Notification).filter(Notification.id == notification_id).first()

        if not notification:
            raise ValueError(f"Notification with id {notification_id} not found")

        notification.is_read = True
        notification.read_at = datetime.utcnow()

        db.commit()
        db.refresh(notification)
        return notification

    @staticmethod
    def delete_notification(db: Session, notification_id: int) -> bool:
        """Delete notification.

        Args:
            db: Database session
            notification_id: Notification ID

        Returns:
            True if deleted, False if not found
        """
        notification = db.query(Notification).filter(Notification.id == notification_id).first()

        if not notification:
            return False

        db.delete(notification)
        db.commit()
        return True
