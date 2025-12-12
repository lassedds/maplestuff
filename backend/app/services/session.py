"""
Session management service for GMSTracker.
Handles user session creation, validation, and cleanup.
"""

import json
import secrets
from datetime import datetime, timedelta
from uuid import UUID

from app.redis import get_redis, RedisKeys
from app.config import settings


# Session settings
SESSION_TTL_SECONDS = 60 * 60 * 24 * 7  # 7 days
SESSION_TOKEN_BYTES = 32


class SessionData:
    """User session data stored in Redis."""

    def __init__(
        self,
        user_id: UUID,
        discord_id: str,
        created_at: datetime | None = None,
        last_accessed: datetime | None = None,
    ):
        self.user_id = user_id
        self.discord_id = discord_id
        self.created_at = created_at or datetime.utcnow()
        self.last_accessed = last_accessed or datetime.utcnow()

    def to_dict(self) -> dict:
        """Convert to dictionary for Redis storage."""
        return {
            "user_id": str(self.user_id),
            "discord_id": self.discord_id,
            "created_at": self.created_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SessionData":
        """Create from dictionary."""
        return cls(
            user_id=UUID(data["user_id"]),
            discord_id=data["discord_id"],
            created_at=datetime.fromisoformat(data["created_at"]),
            last_accessed=datetime.fromisoformat(data["last_accessed"]),
        )


class SessionService:
    """Service for managing user sessions in Redis."""

    @staticmethod
    def generate_token() -> str:
        """Generate a secure session token."""
        return secrets.token_urlsafe(SESSION_TOKEN_BYTES)

    @staticmethod
    async def create(user_id: UUID, discord_id: str) -> str:
        """
        Create a new session for a user.
        Returns the session token.
        """
        redis = get_redis()
        token = SessionService.generate_token()
        session = SessionData(user_id=user_id, discord_id=discord_id)

        key = RedisKeys.session(token)
        await redis.setex(
            key,
            SESSION_TTL_SECONDS,
            json.dumps(session.to_dict()),
        )

        return token

    @staticmethod
    async def get(token: str) -> SessionData | None:
        """
        Get session data by token.
        Updates last_accessed timestamp.
        Returns None if session doesn't exist or is expired.
        """
        redis = get_redis()
        key = RedisKeys.session(token)

        data = await redis.get(key)
        if data is None:
            return None

        session = SessionData.from_dict(json.loads(data))

        # Update last accessed time and refresh TTL
        session.last_accessed = datetime.utcnow()
        await redis.setex(
            key,
            SESSION_TTL_SECONDS,
            json.dumps(session.to_dict()),
        )

        return session

    @staticmethod
    async def delete(token: str) -> bool:
        """
        Delete a session (logout).
        Returns True if session existed.
        """
        redis = get_redis()
        key = RedisKeys.session(token)
        result = await redis.delete(key)
        return result > 0

    @staticmethod
    async def delete_all_for_user(discord_id: str) -> int:
        """
        Delete all sessions for a user (logout everywhere).
        Returns count of deleted sessions.

        Note: This requires scanning all session keys, which can be slow.
        Consider maintaining a user->sessions index for production.
        """
        redis = get_redis()
        pattern = f"{RedisKeys.SESSION}*"
        deleted = 0

        async for key in redis.scan_iter(match=pattern):
            data = await redis.get(key)
            if data:
                session = json.loads(data)
                if session.get("discord_id") == discord_id:
                    await redis.delete(key)
                    deleted += 1

        return deleted
