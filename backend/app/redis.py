"""
Redis client for GMSTracker.
Used for sessions, caching, and rate limiting.
"""

from redis.asyncio import Redis, from_url

from app.config import settings

# Global Redis client (initialized on startup)
redis_client: Redis | None = None


async def init_redis() -> Redis:
    """Initialize Redis connection."""
    global redis_client
    redis_client = await from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
    )
    return redis_client


async def close_redis() -> None:
    """Close Redis connection."""
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None


def get_redis() -> Redis:
    """Get Redis client. Raises if not initialized."""
    if redis_client is None:
        raise RuntimeError("Redis not initialized. Call init_redis() first.")
    return redis_client


# Key prefixes for organization
class RedisKeys:
    """Redis key prefixes for different data types."""

    SESSION = "session:"          # User sessions
    RATE_LIMIT = "ratelimit:"     # Rate limiting counters
    CACHE = "cache:"              # General cache
    JOB = "job:"                  # Background job data

    @classmethod
    def session(cls, session_id: str) -> str:
        """Get session key."""
        return f"{cls.SESSION}{session_id}"

    @classmethod
    def rate_limit(cls, identifier: str, endpoint: str) -> str:
        """Get rate limit key."""
        return f"{cls.RATE_LIMIT}{identifier}:{endpoint}"

    @classmethod
    def cache(cls, key: str) -> str:
        """Get cache key."""
        return f"{cls.CACHE}{key}"
