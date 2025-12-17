"""
Shared FastAPI dependencies for GMSTracker.
"""

import uuid
from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models import User


# Type alias for database session dependency
DBSession = Annotated[AsyncSession, Depends(get_db)]


async def get_session_user_id(request: Request) -> uuid.UUID | None:
    """
    Extract user ID from session cookie.
    Returns None if no valid session.
    """
    from app.services.session import SessionService

    # Get session token from cookie
    session_token = request.cookies.get(settings.session_cookie_name)
    if not session_token:
        return None

    try:
        # Look up session in Redis
        session_data = await SessionService.get(session_token)
        if session_data:
            return session_data.user_id
    except Exception:
        # Redis unavailable or session invalid
        pass

    return None


async def get_current_user_optional(
    request: Request,
    db: DBSession,
) -> User | None:
    """
    Get current user from session.
    Returns None if not authenticated.
    """
    user_id = await get_session_user_id(request)
    if user_id is None:
        return None

    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    return result.scalar_one_or_none()


async def get_current_user(
    request: Request,
    db: DBSession,
) -> User:
    """
    Get current authenticated user.
    Raises 401 if not authenticated.

    Falls back to mock user in debug mode when Redis is unavailable.
about:blank#blocked    TEMPORARY: Always uses mock user when DEBUG=true (no login required).
    """
    # Try to get user from session
    user = await get_current_user_optional(request, db)
    if user:
        return user

    # TEMPORARY: In debug mode, always use mock user (no login required)
    if settings.debug:
        return await _get_or_create_mock_user(db)

    # Not authenticated
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def _get_or_create_mock_user(db: AsyncSession) -> User:
    """
    Get or create a mock user for development.
    Only used when DEBUG=true and no real session exists.
    """
    mock_discord_id = "DEV_USER_123456789"

    result = await db.execute(
        select(User).where(User.discord_id == mock_discord_id)
    )
    user = result.scalar_one_or_none()

    if user is None:
        user = User(
            id=uuid.uuid4(),
            discord_id=mock_discord_id,
            discord_username="DevUser",
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    return user


# Type aliases for dependency injection
CurrentUser = Annotated[User, Depends(get_current_user)]
OptionalUser = Annotated[User | None, Depends(get_current_user_optional)]
