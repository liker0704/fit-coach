"""Notification endpoints."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.notification import Notification
from app.models.user import User
from app.schemas.notification import NotificationResponse, NotificationUpdate
from app.services.notification_service import NotificationService

router = APIRouter()


@router.get("/notifications", response_model=List[NotificationResponse])
def get_notifications(
    unread_only: bool = Query(False, description="Filter to show only unread notifications"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all user's notifications.

    Args:
        unread_only: If True, only return unread notifications (default: False)
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of notifications ordered by created_at desc
    """
    notifications = NotificationService.get_user_notifications(
        db, current_user.id, unread_only=unread_only
    )
    return notifications


@router.get("/notifications/{notification_id}", response_model=NotificationResponse)
def get_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get specific notification by ID.

    Args:
        notification_id: Notification ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Notification data

    Raises:
        HTTPException: 404 if notification not found, 403 if not authorized
    """
    notification = NotificationService.get_notification(db, notification_id)

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification with id {notification_id} not found",
        )

    # Verify notification belongs to current user
    if notification.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this notification",
        )

    return notification


@router.put("/notifications/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark notification as read.

    Args:
        notification_id: Notification ID to mark as read
        db: Database session
        current_user: Current authenticated user

    Returns:
        Updated notification data

    Raises:
        HTTPException: 404 if notification not found, 403 if not authorized
    """
    # First check if notification exists
    notification = db.query(Notification).filter(Notification.id == notification_id).first()

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification with id {notification_id} not found",
        )

    # Verify notification belongs to current user
    if notification.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this notification",
        )

    # Mark as read
    try:
        updated_notification = NotificationService.mark_as_read(db, notification_id)
        return updated_notification
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.delete("/notifications/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete notification.

    Args:
        notification_id: Notification ID to delete
        db: Database session
        current_user: Current authenticated user

    Returns:
        No content (204)

    Raises:
        HTTPException: 404 if notification not found, 403 if not authorized
    """
    # First check if notification exists
    notification = db.query(Notification).filter(Notification.id == notification_id).first()

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification with id {notification_id} not found",
        )

    # Verify notification belongs to current user
    if notification.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this notification",
        )

    # Delete notification
    success = NotificationService.delete_notification(db, notification_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification with id {notification_id} not found",
        )

    return None
