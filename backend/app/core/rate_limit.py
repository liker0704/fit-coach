"""Rate limiting configuration using slowapi."""

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, Response
from fastapi.responses import JSONResponse


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """Custom handler for rate limit exceeded errors.

    Args:
        request: The request that exceeded the rate limit
        exc: The RateLimitExceeded exception

    Returns:
        JSON response with 429 status code
    """
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Rate limit exceeded. Please try again later.",
            "retry_after": exc.retry_after if hasattr(exc, 'retry_after') else None
        },
        headers={"Retry-After": str(exc.retry_after) if hasattr(exc, 'retry_after') else "60"}
    )


# Initialize limiter with remote address as key
limiter = Limiter(key_func=get_remote_address)
