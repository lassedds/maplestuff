"""
Rate limiting service for GMSTracker.
Uses Redis sliding window algorithm.
"""

from datetime import datetime
from functools import wraps
from typing import Callable

from fastapi import HTTPException, Request, status

from app.redis import get_redis, RedisKeys


class RateLimitExceeded(HTTPException):
    """Exception raised when rate limit is exceeded."""

    def __init__(self, retry_after: int):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Try again in {retry_after} seconds.",
            headers={"Retry-After": str(retry_after)},
        )


class RateLimiter:
    """
    Rate limiter using Redis sliding window.

    Usage:
        limiter = RateLimiter(requests=100, window=60)  # 100 req/min
        await limiter.check("user_123", "/api/characters")
    """

    def __init__(self, requests: int, window: int):
        """
        Initialize rate limiter.

        Args:
            requests: Maximum number of requests allowed
            window: Time window in seconds
        """
        self.requests = requests
        self.window = window

    async def check(self, identifier: str, endpoint: str = "global") -> bool:
        """
        Check if request is allowed.

        Args:
            identifier: Unique identifier (user ID, IP, etc.)
            endpoint: Endpoint being accessed (for per-endpoint limits)

        Returns:
            True if allowed

        Raises:
            RateLimitExceeded if limit exceeded
        """
        redis = get_redis()
        key = RedisKeys.rate_limit(identifier, endpoint)
        now = datetime.utcnow().timestamp()
        window_start = now - self.window

        # Use Redis pipeline for atomic operations
        pipe = redis.pipeline()

        # Remove old entries outside window
        pipe.zremrangebyscore(key, 0, window_start)

        # Count requests in current window
        pipe.zcard(key)

        # Add current request with timestamp as score
        pipe.zadd(key, {str(now): now})

        # Set expiry on key
        pipe.expire(key, self.window)

        results = await pipe.execute()
        request_count = results[1]

        if request_count >= self.requests:
            # Calculate retry-after
            oldest = await redis.zrange(key, 0, 0, withscores=True)
            if oldest:
                retry_after = int(oldest[0][1] + self.window - now) + 1
            else:
                retry_after = self.window
            raise RateLimitExceeded(retry_after=retry_after)

        return True

    async def get_remaining(self, identifier: str, endpoint: str = "global") -> int:
        """Get remaining requests in current window."""
        redis = get_redis()
        key = RedisKeys.rate_limit(identifier, endpoint)
        now = datetime.utcnow().timestamp()
        window_start = now - self.window

        # Remove old entries and count
        await redis.zremrangebyscore(key, 0, window_start)
        count = await redis.zcard(key)

        return max(0, self.requests - count)


# Pre-configured rate limiters
default_limiter = RateLimiter(requests=100, window=60)      # 100/min
strict_limiter = RateLimiter(requests=10, window=60)        # 10/min (for auth)
lenient_limiter = RateLimiter(requests=1000, window=60)     # 1000/min (for reads)


def get_client_identifier(request: Request) -> str:
    """
    Get unique identifier for rate limiting.
    Uses user ID if authenticated, otherwise IP address.
    """
    # Check for authenticated user (set by auth middleware)
    if hasattr(request.state, "user") and request.state.user:
        return f"user:{request.state.user.id}"

    # Fall back to IP address
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        ip = forwarded.split(",")[0].strip()
    else:
        ip = request.client.host if request.client else "unknown"

    return f"ip:{ip}"


async def check_rate_limit(
    request: Request,
    limiter: RateLimiter = default_limiter,
) -> None:
    """
    Dependency to check rate limit.

    Usage:
        @router.get("/endpoint")
        async def endpoint(
            _: None = Depends(lambda r: check_rate_limit(r, strict_limiter))
        ):
            ...
    """
    identifier = get_client_identifier(request)
    endpoint = request.url.path
    await limiter.check(identifier, endpoint)
