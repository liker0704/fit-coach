"""LLM-specific rate limiter for FitCoach API.

This module provides specialized rate limiting for LLM API calls to:
1. Prevent abuse and excessive costs
2. Ensure fair usage across users
3. Protect against DoS attacks targeting expensive LLM operations

Unlike general API rate limiting, this focuses specifically on LLM calls
which are the most expensive operations in the system.

Features:
- Redis-based distributed rate limiting
- Per-user hourly and per-minute limits
- Per-agent-type granularity
- Informative rate limit headers
- Graceful error messages
- Automatic cleanup of expired keys
"""

import logging
import time
from typing import Optional, Tuple

from fastapi import HTTPException, Request, status
from redis import Redis
from redis.exceptions import ConnectionError as RedisConnectionError

from app.config import settings

logger = logging.getLogger(__name__)


class LLMRateLimiter:
    """Rate limiter for LLM API calls.

    Implements a sliding window rate limiter using Redis to track:
    - Hourly limits per user (to prevent cost abuse)
    - Per-minute limits per agent per user (to prevent spam)

    Example:
        ```python
        limiter = LLMRateLimiter(redis_client)

        # Check rate limit before LLM call
        await limiter.check_rate_limit(
            user_id=123,
            agent_type="nutrition_coach"
        )

        # Make LLM call...

        # Optionally, get remaining quota
        remaining = limiter.get_remaining(user_id=123)
        ```
    """

    # Default rate limits
    DEFAULT_HOURLY_LIMIT = 50  # 50 LLM requests per hour per user
    DEFAULT_PER_MINUTE_LIMIT = 10  # 10 requests per minute per agent per user

    # Redis key prefixes
    HOURLY_KEY_PREFIX = "llm_rate:hourly:"
    MINUTE_KEY_PREFIX = "llm_rate:minute:"

    def __init__(
        self,
        redis_client: Optional[Redis] = None,
        hourly_limit: int = DEFAULT_HOURLY_LIMIT,
        per_minute_limit: int = DEFAULT_PER_MINUTE_LIMIT,
    ):
        """Initialize LLM rate limiter.

        Args:
            redis_client: Redis client (if None, will create from settings)
            hourly_limit: Max LLM requests per hour per user (default: 50)
            per_minute_limit: Max requests per minute per agent per user (default: 10)
        """
        self.redis_client = redis_client or self._create_redis_client()
        self.hourly_limit = hourly_limit
        self.per_minute_limit = per_minute_limit

    def _create_redis_client(self) -> Redis:
        """Create Redis client from settings.

        Returns:
            Redis client instance

        Raises:
            ValueError: If Redis connection fails
        """
        try:
            client = Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD if hasattr(settings, 'REDIS_PASSWORD') else None,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5,
            )
            # Test connection
            client.ping()
            logger.info("LLM rate limiter connected to Redis")
            return client
        except Exception as e:
            logger.error(f"Failed to connect to Redis for rate limiting: {e}")
            raise ValueError(f"Redis connection failed: {e}")

    def _get_hourly_key(self, user_id: int) -> str:
        """Get Redis key for hourly limit.

        Args:
            user_id: User ID

        Returns:
            Redis key string
        """
        # Use hour-based key for sliding window
        current_hour = int(time.time() / 3600)
        return f"{self.HOURLY_KEY_PREFIX}{user_id}:{current_hour}"

    def _get_minute_key(self, user_id: int, agent_type: str) -> str:
        """Get Redis key for per-minute limit.

        Args:
            user_id: User ID
            agent_type: Agent type (e.g., 'nutrition_coach')

        Returns:
            Redis key string
        """
        # Use minute-based key for sliding window
        current_minute = int(time.time() / 60)
        return f"{self.MINUTE_KEY_PREFIX}{user_id}:{agent_type}:{current_minute}"

    def _check_limit(
        self,
        key: str,
        limit: int,
        ttl: int,
    ) -> Tuple[bool, int, int]:
        """Check and increment a rate limit counter.

        Args:
            key: Redis key
            limit: Maximum allowed count
            ttl: Time-to-live in seconds

        Returns:
            Tuple of (allowed, current_count, reset_time)
            - allowed: True if under limit
            - current_count: Current count for this window
            - reset_time: Unix timestamp when limit resets
        """
        try:
            # Increment counter
            current = self.redis_client.incr(key)

            # Set expiry on first increment
            if current == 1:
                self.redis_client.expire(key, ttl)

            # Get TTL for reset time calculation
            remaining_ttl = self.redis_client.ttl(key)
            reset_time = int(time.time()) + max(remaining_ttl, 0)

            # Check if over limit
            allowed = current <= limit

            return allowed, current, reset_time

        except RedisConnectionError as e:
            logger.error(f"Redis connection error in rate limiter: {e}")
            # Fail open - allow request if Redis is down
            return True, 0, 0

        except Exception as e:
            logger.error(f"Unexpected error in rate limiter: {e}")
            # Fail open
            return True, 0, 0

    async def check_rate_limit(
        self,
        user_id: int,
        agent_type: str,
    ) -> None:
        """Check rate limits for LLM request.

        Checks both hourly and per-minute limits. Raises HTTPException if exceeded.

        Args:
            user_id: User ID making the request
            agent_type: Type of agent being called

        Raises:
            HTTPException: 429 if rate limit exceeded
        """
        # Check hourly limit
        hourly_key = self._get_hourly_key(user_id)
        hourly_allowed, hourly_count, hourly_reset = self._check_limit(
            hourly_key,
            self.hourly_limit,
            ttl=3600  # 1 hour
        )

        if not hourly_allowed:
            logger.warning(
                f"Hourly LLM rate limit exceeded for user {user_id}. "
                f"Count: {hourly_count}/{self.hourly_limit}"
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "rate_limit_exceeded",
                    "message": f"Hourly LLM request limit exceeded. "
                               f"Limit: {self.hourly_limit} requests per hour. "
                               f"Please try again later.",
                    "limit": self.hourly_limit,
                    "remaining": 0,
                    "reset": hourly_reset,
                },
                headers={
                    "X-RateLimit-Limit": str(self.hourly_limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(hourly_reset),
                    "Retry-After": str(max(hourly_reset - int(time.time()), 0)),
                },
            )

        # Check per-minute limit
        minute_key = self._get_minute_key(user_id, agent_type)
        minute_allowed, minute_count, minute_reset = self._check_limit(
            minute_key,
            self.per_minute_limit,
            ttl=60  # 1 minute
        )

        if not minute_allowed:
            logger.warning(
                f"Per-minute LLM rate limit exceeded for user {user_id} "
                f"and agent {agent_type}. "
                f"Count: {minute_count}/{self.per_minute_limit}"
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "rate_limit_exceeded",
                    "message": f"Too many requests to {agent_type}. "
                               f"Limit: {self.per_minute_limit} requests per minute. "
                               f"Please slow down.",
                    "limit": self.per_minute_limit,
                    "remaining": 0,
                    "reset": minute_reset,
                },
                headers={
                    "X-RateLimit-Limit": str(self.per_minute_limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(minute_reset),
                    "Retry-After": str(max(minute_reset - int(time.time()), 0)),
                },
            )

        # Log successful check (for monitoring)
        logger.debug(
            f"LLM rate limit check passed for user {user_id}, agent {agent_type}. "
            f"Hourly: {hourly_count}/{self.hourly_limit}, "
            f"Minute: {minute_count}/{self.per_minute_limit}"
        )

    def get_remaining(
        self,
        user_id: int,
        agent_type: Optional[str] = None,
    ) -> dict:
        """Get remaining quota for user.

        Args:
            user_id: User ID
            agent_type: Optional agent type for per-minute quota

        Returns:
            Dictionary with quota information
        """
        try:
            hourly_key = self._get_hourly_key(user_id)
            hourly_count = int(self.redis_client.get(hourly_key) or 0)
            hourly_remaining = max(self.hourly_limit - hourly_count, 0)

            result = {
                "hourly_limit": self.hourly_limit,
                "hourly_remaining": hourly_remaining,
                "hourly_used": hourly_count,
            }

            if agent_type:
                minute_key = self._get_minute_key(user_id, agent_type)
                minute_count = int(self.redis_client.get(minute_key) or 0)
                minute_remaining = max(self.per_minute_limit - minute_count, 0)

                result.update({
                    "minute_limit": self.per_minute_limit,
                    "minute_remaining": minute_remaining,
                    "minute_used": minute_count,
                    "agent_type": agent_type,
                })

            return result

        except Exception as e:
            logger.error(f"Error getting remaining quota: {e}")
            return {
                "hourly_limit": self.hourly_limit,
                "hourly_remaining": self.hourly_limit,
                "hourly_used": 0,
            }

    def reset_user_limits(self, user_id: int) -> None:
        """Reset all limits for a user.

        Useful for testing or admin operations.

        Args:
            user_id: User ID to reset
        """
        try:
            # Find and delete all keys for this user
            hourly_pattern = f"{self.HOURLY_KEY_PREFIX}{user_id}:*"
            minute_pattern = f"{self.MINUTE_KEY_PREFIX}{user_id}:*"

            for pattern in [hourly_pattern, minute_pattern]:
                keys = self.redis_client.keys(pattern)
                if keys:
                    self.redis_client.delete(*keys)

            logger.info(f"Reset LLM rate limits for user {user_id}")

        except Exception as e:
            logger.error(f"Error resetting limits for user {user_id}: {e}")


# Global singleton instance
_limiter: Optional[LLMRateLimiter] = None


def get_llm_limiter() -> LLMRateLimiter:
    """Get the global LLM rate limiter instance.

    Returns:
        LLMRateLimiter instance

    Raises:
        ValueError: If Redis connection fails
    """
    global _limiter
    if _limiter is None:
        _limiter = LLMRateLimiter()
    return _limiter


async def check_llm_rate_limit(user_id: int, agent_type: str) -> None:
    """Convenience function to check LLM rate limit.

    Args:
        user_id: User ID
        agent_type: Agent type

    Raises:
        HTTPException: 429 if rate limit exceeded
    """
    limiter = get_llm_limiter()
    await limiter.check_rate_limit(user_id, agent_type)
