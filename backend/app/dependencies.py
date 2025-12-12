"""
Shared FastAPI dependencies for GMSTracker.
"""

import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User


# Type alias for database session dependency
DBSession = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user_optional(db: DBSession) -> User | None:
    """
    Get current user from session.
    Returns None if not authenticated.

    TODO: Implement actual session/token lookup in Step 6-9.
    For now, returns None (no auth).
    """
    return None


async def get_current_user(db: DBSession) -> User:
    """
    Get current authenticated user.
    Raises 401 if not authenticated.

    TODO: Implement actual session/token lookup in Step 6-9.
    For now, uses mock user for development.
    """
    # MOCK USER FOR DEVELOPMENT
    # This will be replaced with actual auth in Steps 6-9
    mock_discord_id = "DEV_USER_123456789"

    # Try to get existing mock user
    result = await db.execute(
        select(User).where(User.discord_id == mock_discord_id)
    )
    user = result.scalar_one_or_none()

    if user is None:
        # Create mock user for development
        user = User(
            id=uuid.uuid4(),
            discord_id=mock_discord_id,
            discord_username="DevUser",
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    return user


# Type alias for current user dependency
CurrentUser = Annotated[User, Depends(get_current_user)]
