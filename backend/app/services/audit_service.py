"""Audit logging service for tracking security events."""

import logging
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import Request
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog

logger = logging.getLogger(__name__)


class AuditService:
    """Service for logging security-relevant events."""

    # Event types
    EVENT_LOGIN = "login"
    EVENT_LOGIN_FAILED = "login_failed"
    EVENT_LOGOUT = "logout"
    EVENT_LOGOUT_ALL = "logout_all"
    EVENT_REGISTER = "register"
    EVENT_PASSWORD_RESET_REQUEST = "password_reset_request"
    EVENT_PASSWORD_RESET_COMPLETE = "password_reset_complete"
    EVENT_PASSWORD_CHANGE = "password_change"
    EVENT_EMAIL_VERIFICATION_REQUEST = "email_verification_request"
    EVENT_EMAIL_VERIFICATION_COMPLETE = "email_verification_complete"
    EVENT_PROFILE_UPDATE = "profile_update"
    EVENT_ACCOUNT_DELETE = "account_delete"
    EVENT_TOKEN_REFRESH = "token_refresh"
    EVENT_RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"

    # Event categories
    CATEGORY_AUTH = "auth"
    CATEGORY_PROFILE = "profile"
    CATEGORY_DATA = "data"
    CATEGORY_SECURITY = "security"

    # Status
    STATUS_SUCCESS = "success"
    STATUS_FAILURE = "failure"

    @staticmethod
    def _get_client_ip(request: Optional[Request]) -> Optional[str]:
        """Extract client IP address from request.

        Args:
            request: FastAPI request object

        Returns:
            Client IP address or None
        """
        if not request:
            return None

        # Check for X-Forwarded-For header (if behind proxy)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        # Check for X-Real-IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fall back to client host
        if request.client:
            return request.client.host

        return None

    @staticmethod
    def _get_user_agent(request: Optional[Request]) -> Optional[str]:
        """Extract user agent from request.

        Args:
            request: FastAPI request object

        Returns:
            User agent string or None
        """
        if not request:
            return None
        return request.headers.get("User-Agent")

    @staticmethod
    def log_event(
        db: Session,
        event_type: str,
        event_category: str,
        status: str,
        user_id: Optional[int] = None,
        description: Optional[str] = None,
        request: Optional[Request] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AuditLog:
        """Log a security event to the audit log.

        Args:
            db: Database session
            event_type: Type of event (e.g., "login", "logout")
            event_category: Category of event (e.g., "auth", "profile")
            status: Event status ("success" or "failure")
            user_id: User ID associated with the event (if applicable)
            description: Human-readable description of the event
            request: FastAPI request object (for IP and user agent)
            metadata: Additional context data as dictionary

        Returns:
            Created AuditLog instance
        """
        try:
            # Extract request data
            ip_address = AuditService._get_client_ip(request)
            user_agent = AuditService._get_user_agent(request)

            # Create audit log entry
            audit_log = AuditLog(
                user_id=user_id,
                event_type=event_type,
                event_category=event_category,
                description=description,
                ip_address=ip_address,
                user_agent=user_agent,
                metadata=metadata,
                status=status,
                created_at=datetime.utcnow(),
            )

            db.add(audit_log)
            db.commit()
            db.refresh(audit_log)

            logger.info(
                f"Audit log created: event={event_type}, category={event_category}, "
                f"status={status}, user_id={user_id}, ip={ip_address}"
            )

            return audit_log

        except Exception as e:
            logger.error(f"Failed to create audit log: {str(e)}")
            db.rollback()
            raise

    @staticmethod
    def log_login_success(
        db: Session,
        user_id: int,
        email: str,
        request: Optional[Request] = None,
    ) -> None:
        """Log successful login.

        Args:
            db: Database session
            user_id: User ID
            email: User email
            request: FastAPI request object
        """
        AuditService.log_event(
            db=db,
            event_type=AuditService.EVENT_LOGIN,
            event_category=AuditService.CATEGORY_AUTH,
            status=AuditService.STATUS_SUCCESS,
            user_id=user_id,
            description=f"User {email} logged in successfully",
            request=request,
        )

    @staticmethod
    def log_login_failure(
        db: Session,
        email: str,
        reason: str,
        request: Optional[Request] = None,
    ) -> None:
        """Log failed login attempt.

        Args:
            db: Database session
            email: Email used in login attempt
            reason: Reason for failure
            request: FastAPI request object
        """
        AuditService.log_event(
            db=db,
            event_type=AuditService.EVENT_LOGIN_FAILED,
            event_category=AuditService.CATEGORY_SECURITY,
            status=AuditService.STATUS_FAILURE,
            description=f"Failed login attempt for {email}: {reason}",
            request=request,
            metadata={"email": email, "reason": reason},
        )

    @staticmethod
    def log_logout(
        db: Session,
        user_id: int,
        email: str,
        request: Optional[Request] = None,
    ) -> None:
        """Log user logout.

        Args:
            db: Database session
            user_id: User ID
            email: User email
            request: FastAPI request object
        """
        AuditService.log_event(
            db=db,
            event_type=AuditService.EVENT_LOGOUT,
            event_category=AuditService.CATEGORY_AUTH,
            status=AuditService.STATUS_SUCCESS,
            user_id=user_id,
            description=f"User {email} logged out",
            request=request,
        )

    @staticmethod
    def log_password_reset_request(
        db: Session,
        email: str,
        request: Optional[Request] = None,
    ) -> None:
        """Log password reset request.

        Args:
            db: Database session
            email: Email requesting password reset
            request: FastAPI request object
        """
        AuditService.log_event(
            db=db,
            event_type=AuditService.EVENT_PASSWORD_RESET_REQUEST,
            event_category=AuditService.CATEGORY_SECURITY,
            status=AuditService.STATUS_SUCCESS,
            description=f"Password reset requested for {email}",
            request=request,
            metadata={"email": email},
        )

    @staticmethod
    def log_password_reset_complete(
        db: Session,
        user_id: int,
        email: str,
        request: Optional[Request] = None,
    ) -> None:
        """Log completed password reset.

        Args:
            db: Database session
            user_id: User ID
            email: User email
            request: FastAPI request object
        """
        AuditService.log_event(
            db=db,
            event_type=AuditService.EVENT_PASSWORD_RESET_COMPLETE,
            event_category=AuditService.CATEGORY_SECURITY,
            status=AuditService.STATUS_SUCCESS,
            user_id=user_id,
            description=f"Password reset completed for {email}",
            request=request,
        )

    @staticmethod
    def log_registration(
        db: Session,
        user_id: int,
        email: str,
        request: Optional[Request] = None,
    ) -> None:
        """Log new user registration.

        Args:
            db: Database session
            user_id: New user ID
            email: User email
            request: FastAPI request object
        """
        AuditService.log_event(
            db=db,
            event_type=AuditService.EVENT_REGISTER,
            event_category=AuditService.CATEGORY_AUTH,
            status=AuditService.STATUS_SUCCESS,
            user_id=user_id,
            description=f"New user registered: {email}",
            request=request,
        )
