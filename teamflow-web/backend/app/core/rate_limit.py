"""T163: Rate limiting utilities for API endpoints.

This module provides in-memory rate limiting using a sliding window algorithm.
For production, consider using Redis for distributed rate limiting.
"""
import time
from collections import defaultdict
from dataclasses import dataclass
from functools import wraps
from typing import Callable

from fastapi import HTTPException, Request


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""
    max_requests: int  # Maximum requests allowed
    window_seconds: int  # Time window in seconds


# Rate limit configurations for different endpoints
RATE_LIMITS = {
    "auth_login": RateLimitConfig(max_requests=5, window_seconds=60),  # 5 login attempts per minute
    "auth_register": RateLimitConfig(max_requests=3, window_seconds=3600),  # 3 registrations per hour
    "auth_default": RateLimitConfig(max_requests=20, window_seconds=60),  # Default: 20 requests per minute
}


class InMemoryRateLimiter:
    """In-memory rate limiter using sliding window algorithm.

    Note: For production with multiple workers, use Redis-based rate limiting.
    """

    def __init__(self):
        # Store request timestamps per key (IP address or endpoint)
        self.requests: defaultdict[str, list[float]] = defaultdict(list)

    def is_allowed(
        self,
        key: str,
        config: RateLimitConfig,
    ) -> bool:
        """Check if request is allowed under rate limit.

        Args:
            key: Unique identifier for rate limiting (e.g., IP address)
            config: Rate limit configuration

        Returns:
            True if request is allowed, False otherwise
        """
        now = time.time()
        window_start = now - config.window_seconds

        # Get existing requests for this key
        request_times = self.requests[key]

        # Filter out requests outside the time window
        request_times = [t for t in request_times if t > window_start]
        self.requests[key] = request_times

        # Check if under limit
        if len(request_times) < config.max_requests:
            request_times.append(now)
            return True

        return False

    def get_retry_after(
        self,
        key: str,
        config: RateLimitConfig,
    ) -> int:
        """Get seconds until next request is allowed.

        Args:
            key: Unique identifier for rate limiting
            config: Rate limit configuration

        Returns:
            Seconds until next allowed request
        """
        request_times = self.requests[key]
        if not request_times:
            return 0

        # The oldest request in the current window
        oldest_request = min(request_times)
        window_start = time.time() - config.window_seconds

        # If oldest request is outside window, no retry needed
        if oldest_request < window_start:
            return 0

        # Otherwise, calculate when it expires
        return int(oldest_request + config.window_seconds - time.time()) + 1


# Global rate limiter instance
rate_limiter = InMemoryRateLimiter()


def get_client_identifier(request: Request) -> str:
    """Get a unique identifier for rate limiting.

    Uses X-Forwarded-For header if available (for production behind proxy),
    otherwise falls back to client IP.
    """
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    return request.client.host if request.client else "unknown"


def rate_limit(limit_type: str = "auth_default"):
    """Decorator for rate limiting endpoints.

    Args:
        limit_type: Type of rate limit to apply (from RATE_LIMITS)

    Example:
        @rate_limit("auth_login")
        @router.post("/login")
        async def login(...):
            ...
    """
    config = RATE_LIMITS.get(limit_type, RATE_LIMITS["auth_default"])

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            # Get client identifier for rate limiting
            client_id = get_client_identifier(request)
            rate_limit_key = f"{limit_type}:{client_id}"

            # Check if request is allowed
            if not rate_limiter.is_allowed(rate_limit_key, config):
                retry_after = rate_limiter.get_retry_after(rate_limit_key, config)
                raise HTTPException(
                    status_code=429,
                    detail={
                        "error": "Too many requests",
                        "retry_after": retry_after,
                    },
                    headers={"Retry-After": str(retry_after)},
                )

            return await func(request, *args, **kwargs)

        return wrapper
    return decorator


def check_rate_limit(
    request: Request,
    limit_type: str = "auth_default",
) -> None:
    """Check rate limit and raise exception if exceeded.

    Helper function for use inside endpoints.

    Args:
        request: FastAPI Request object
        limit_type: Type of rate limit to apply

    Raises:
        HTTPException: If rate limit exceeded
    """
    config = RATE_LIMITS.get(limit_type, RATE_LIMITS["auth_default"])
    client_id = get_client_identifier(request)
    rate_limit_key = f"{limit_type}:{client_id}"

    if not rate_limiter.is_allowed(rate_limit_key, config):
        retry_after = rate_limiter.get_retry_after(rate_limit_key, config)
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Too many requests",
                "retry_after": retry_after,
            },
            headers={"Retry-After": str(retry_after)},
        )
