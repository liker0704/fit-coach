"""CSRF protection middleware for FitCoach API.

This module provides CSRF (Cross-Site Request Forgery) protection for the application.
While JWT Bearer tokens provide inherent CSRF protection for API endpoints,
this middleware adds an additional layer of security for future cookie-based authentication.

Key features:
- CSRF token generation and validation
- Automatic exemption for Bearer token authenticated requests
- Configurable for safe methods (GET, HEAD, OPTIONS, TRACE)
- SameSite cookie configuration for additional protection
"""

import logging
import secrets
from typing import Callable, Optional

from fastapi import HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class CSRFProtection(BaseHTTPMiddleware):
    """CSRF protection middleware.

    Protects against Cross-Site Request Forgery attacks by validating
    CSRF tokens for state-changing requests (POST, PUT, DELETE, PATCH).

    Attributes:
        secret_key: Secret key for token generation
        cookie_name: Name of the CSRF cookie
        header_name: Name of the CSRF header
        safe_methods: HTTP methods that don't require CSRF protection
    """

    # Safe methods that don't modify state
    SAFE_METHODS = {"GET", "HEAD", "OPTIONS", "TRACE"}

    # Paths that are exempt from CSRF protection (API with Bearer tokens)
    EXEMPT_PATHS = {
        "/api/v1/auth/login",
        "/api/v1/auth/register",
        "/api/v1/auth/refresh",
        "/docs",
        "/openapi.json",
        "/health",
    }

    def __init__(
        self,
        app,
        secret_key: str,
        cookie_name: str = "csrf_token",
        header_name: str = "X-CSRF-Token",
        cookie_samesite: str = "strict",
        cookie_secure: bool = True,
    ):
        """Initialize CSRF protection middleware.

        Args:
            app: FastAPI application
            secret_key: Secret key for token generation
            cookie_name: Name of the CSRF cookie (default: csrf_token)
            header_name: Name of the CSRF header (default: X-CSRF-Token)
            cookie_samesite: SameSite cookie attribute (default: strict)
            cookie_secure: Whether to use secure cookies (default: True)
        """
        super().__init__(app)
        self.secret_key = secret_key
        self.cookie_name = cookie_name
        self.header_name = header_name
        self.cookie_samesite = cookie_samesite
        self.cookie_secure = cookie_secure

    def generate_csrf_token(self) -> str:
        """Generate a cryptographically secure CSRF token.

        Returns:
            32-byte random token in hexadecimal format
        """
        return secrets.token_hex(32)

    def _is_exempt_path(self, path: str) -> bool:
        """Check if path is exempt from CSRF protection.

        Args:
            path: Request path

        Returns:
            True if path is exempt, False otherwise
        """
        # Check exact matches
        if path in self.EXEMPT_PATHS:
            return True

        # Check prefix matches (e.g., /docs/, /api/v1/auth/)
        for exempt_path in self.EXEMPT_PATHS:
            if path.startswith(exempt_path + "/"):
                return True

        return False

    def _has_bearer_token(self, request: Request) -> bool:
        """Check if request has Bearer token authentication.

        Args:
            request: HTTP request

        Returns:
            True if Bearer token is present, False otherwise
        """
        auth_header = request.headers.get("Authorization", "")
        return auth_header.startswith("Bearer ")

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        """Process request with CSRF protection.

        Args:
            request: HTTP request
            call_next: Next middleware in chain

        Returns:
            HTTP response

        Raises:
            HTTPException: 403 if CSRF validation fails
        """
        # Skip CSRF for safe methods
        if request.method in self.SAFE_METHODS:
            response = await call_next(request)
            return response

        # Skip CSRF for exempt paths
        if self._is_exempt_path(request.url.path):
            response = await call_next(request)
            return response

        # Skip CSRF for Bearer token authenticated requests
        # (JWT Bearer tokens are not vulnerable to CSRF)
        if self._has_bearer_token(request):
            response = await call_next(request)
            return response

        # Validate CSRF token for state-changing methods
        cookie_token = request.cookies.get(self.cookie_name)
        header_token = request.headers.get(self.header_name)

        if not cookie_token:
            logger.warning(
                f"CSRF validation failed: No CSRF cookie present "
                f"for {request.method} {request.url.path}"
            )
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "detail": "CSRF token missing in cookies. Please obtain a new token."
                },
            )

        if not header_token:
            logger.warning(
                f"CSRF validation failed: No CSRF header present "
                f"for {request.method} {request.url.path}"
            )
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "detail": f"CSRF token missing in {self.header_name} header."
                },
            )

        # Validate token match
        if not secrets.compare_digest(cookie_token, header_token):
            logger.warning(
                f"CSRF validation failed: Token mismatch "
                f"for {request.method} {request.url.path}"
            )
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "detail": "CSRF token validation failed. Token mismatch."
                },
            )

        # Token is valid, process request
        response = await call_next(request)
        return response

    def set_csrf_cookie(
        self,
        response: Response,
        token: Optional[str] = None,
    ) -> Response:
        """Set CSRF token cookie on response.

        Args:
            response: HTTP response
            token: CSRF token (generates new one if not provided)

        Returns:
            Response with CSRF cookie set
        """
        if token is None:
            token = self.generate_csrf_token()

        response.set_cookie(
            key=self.cookie_name,
            value=token,
            httponly=True,  # Prevent JavaScript access
            secure=self.cookie_secure,  # HTTPS only in production
            samesite=self.cookie_samesite,  # Prevent CSRF
            max_age=3600 * 24,  # 24 hours
        )

        return response


def get_csrf_token(request: Request) -> Optional[str]:
    """Get CSRF token from request cookies.

    Helper function to retrieve the current CSRF token.

    Args:
        request: HTTP request

    Returns:
        CSRF token if present, None otherwise
    """
    return request.cookies.get("csrf_token")


def generate_csrf_token() -> str:
    """Generate a new CSRF token.

    Helper function for manual token generation.

    Returns:
        32-byte random token in hexadecimal format
    """
    return secrets.token_hex(32)
