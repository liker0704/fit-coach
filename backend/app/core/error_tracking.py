"""Error tracking and Sentry integration."""

import logging
import os
from typing import Any, Dict, Optional

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.request_id import get_request_id

logger = logging.getLogger(__name__)

# Sentry SDK (optional)
sentry_sdk = None
SENTRY_ENABLED = False

try:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

    SENTRY_DSN = os.getenv("SENTRY_DSN")
    SENTRY_ENVIRONMENT = os.getenv("SENTRY_ENVIRONMENT", "development")

    if SENTRY_DSN:
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            environment=SENTRY_ENVIRONMENT,
            traces_sample_rate=0.1,  # 10% of transactions for performance monitoring
            profiles_sample_rate=0.1,  # 10% for profiling
            integrations=[
                FastApiIntegration(),
                SqlalchemyIntegration(),
            ],
            # Filter sensitive data
            before_send=lambda event, hint: filter_sensitive_data(event),
        )
        SENTRY_ENABLED = True
        logger.info(
            "Sentry initialized",
            extra={
                "environment": SENTRY_ENVIRONMENT,
                "traces_sample_rate": 0.1,
            },
        )
except ImportError:
    logger.info("Sentry SDK not installed, error tracking disabled")
except Exception as e:
    logger.warning(f"Failed to initialize Sentry: {e}")


def filter_sensitive_data(event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Filter sensitive data from Sentry events.

    Removes or masks:
    - Passwords
    - API keys
    - Authorization headers
    - Secret keys

    Args:
        event: Sentry event dictionary

    Returns:
        Filtered event or None to drop event
    """
    # List of sensitive keys to filter
    sensitive_keys = {
        "password",
        "secret",
        "api_key",
        "apikey",
        "token",
        "authorization",
        "auth",
        "jwt",
        "refresh_token",
        "access_token",
    }

    def filter_dict(data: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively filter dictionary."""
        filtered = {}
        for key, value in data.items():
            key_lower = key.lower()
            if any(sensitive in key_lower for sensitive in sensitive_keys):
                filtered[key] = "[FILTERED]"
            elif isinstance(value, dict):
                filtered[key] = filter_dict(value)
            elif isinstance(value, list):
                filtered[key] = [
                    filter_dict(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                filtered[key] = value
        return filtered

    # Filter request data
    if "request" in event:
        if "data" in event["request"]:
            event["request"]["data"] = filter_dict(event["request"]["data"])
        if "headers" in event["request"]:
            event["request"]["headers"] = filter_dict(event["request"]["headers"])

    # Filter extra context
    if "extra" in event:
        event["extra"] = filter_dict(event["extra"])

    return event


def capture_exception(
    exception: Exception,
    user_id: Optional[int] = None,
    extra_context: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Capture exception with context.

    Args:
        exception: Exception to capture
        user_id: Optional user ID for context
        extra_context: Additional context data
    """
    request_id = get_request_id()

    # Build context
    context = {
        "request_id": request_id,
    }

    if user_id:
        context["user_id"] = user_id

    if extra_context:
        context.update(extra_context)

    # Log error
    logger.error(
        f"Exception captured: {type(exception).__name__}",
        extra=context,
        exc_info=exception,
    )

    # Send to Sentry if enabled
    if SENTRY_ENABLED and sentry_sdk:
        with sentry_sdk.push_scope() as scope:
            # Set user context
            if user_id:
                scope.set_user({"id": user_id})

            # Set tags
            scope.set_tag("request_id", request_id)

            # Set extra context
            for key, value in context.items():
                scope.set_extra(key, value)

            # Capture exception
            sentry_sdk.capture_exception(exception)


async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    """
    Handle HTTP exceptions with logging.

    Args:
        request: FastAPI request
        exc: HTTP exception

    Returns:
        JSON response with error details
    """
    request_id = get_request_id()

    # Log the error (but not for 404s to avoid spam)
    if exc.status_code >= 500:
        logger.error(
            "HTTP exception",
            extra={
                "request_id": request_id,
                "status_code": exc.status_code,
                "detail": exc.detail,
                "method": request.method,
                "path": request.url.path,
            },
            exc_info=True,
        )

        # Capture in Sentry for 5xx errors
        capture_exception(exc, extra_context={"status_code": exc.status_code})

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "request_id": request_id,
        },
        headers={"X-Request-ID": request_id},
    )


async def general_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """
    Handle all unhandled exceptions.

    Args:
        request: FastAPI request
        exc: Unhandled exception

    Returns:
        JSON response with generic error message
    """
    request_id = get_request_id()

    # Log the error with full traceback
    logger.error(
        "Unhandled exception",
        extra={
            "request_id": request_id,
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            "method": request.method,
            "path": request.url.path,
        },
        exc_info=True,
    )

    # Capture in Sentry
    capture_exception(exc)

    # Return generic error message (don't expose internal details)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later.",
            "request_id": request_id,
        },
        headers={"X-Request-ID": request_id},
    )
