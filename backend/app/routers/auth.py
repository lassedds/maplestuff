"""
Authentication API endpoints for GMSTracker.
Handles Discord OAuth login/logout flow.
"""

from fastapi import APIRouter, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy import select

from app.config import settings
from app.dependencies import DBSession, CurrentUser
from app.models import User, UserSettings
from app.schemas import UserResponse
from app.services.discord_oauth import discord_oauth, DiscordOAuthError
from app.services.session import SessionService
from app.redis import get_redis, RedisKeys

router = APIRouter(prefix="/auth", tags=["auth"])

# Store OAuth states temporarily in Redis (5 min TTL)
OAUTH_STATE_TTL = 300


@router.get("/discord")
async def discord_login(request: Request):
    """
    Start Discord OAuth flow.
    Redirects to Discord authorization page.
    """
    # Generate authorization URL with state
    auth_url, state = discord_oauth.get_authorization_url()

    # Store state in Redis for verification
    try:
        redis = get_redis()
        await redis.setex(
            f"{RedisKeys.CACHE}oauth_state:{state}",
            OAUTH_STATE_TTL,
            "valid",
        )
    except Exception:
        # If Redis unavailable, continue without state verification
        pass

    return RedirectResponse(url=auth_url)


@router.get("/discord/callback")
async def discord_callback(
    code: str,
    state: str,
    db: DBSession,
    response: Response,
):
    """
    Handle Discord OAuth callback.
    Exchanges code for tokens, creates/updates user, creates session.
    """
    # Verify state (CSRF protection)
    try:
        redis = get_redis()
        state_key = f"{RedisKeys.CACHE}oauth_state:{state}"
        valid = await redis.get(state_key)
        if valid:
            await redis.delete(state_key)
        # Note: We don't fail if state is missing (Redis may be unavailable)
    except Exception:
        pass

    # Exchange code for tokens
    try:
        tokens = await discord_oauth.exchange_code(code)
    except DiscordOAuthError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth error: {e}",
        )

    # Get user info from Discord
    try:
        discord_user = await discord_oauth.get_user_info(tokens["access_token"])
    except DiscordOAuthError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get user info: {e}",
        )

    # Find or create user in database
    result = await db.execute(
        select(User).where(User.discord_id == discord_user.id)
    )
    user = result.scalar_one_or_none()

    if user is None:
        # Create new user
        user = User(
            discord_id=discord_user.id,
            discord_username=discord_user.display_name,
            discord_avatar=discord_user.avatar,
        )
        db.add(user)
        await db.flush()

        # Create default settings
        user_settings = UserSettings(
            user_id=user.id,
            timezone="UTC",
            theme="dark",
        )
        db.add(user_settings)
    else:
        # Update existing user info
        user.discord_username = discord_user.display_name
        user.discord_avatar = discord_user.avatar

    await db.commit()
    await db.refresh(user)

    # Create session
    try:
        session_token = await SessionService.create(
            user_id=user.id,
            discord_id=user.discord_id,
        )

        # Set session cookie
        response = RedirectResponse(
            url=settings.frontend_url,
            status_code=status.HTTP_302_FOUND,
        )
        response.set_cookie(
            key=settings.session_cookie_name,
            value=session_token,
            httponly=True,
            secure=not settings.debug,  # Secure in production
            samesite="lax",
            max_age=settings.session_ttl_seconds,
        )

        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create session: {e}",
        )


@router.post("/logout")
async def logout(request: Request, response: Response):
    """
    Log out the current user.
    Clears session and cookie.
    """
    # Get session token from cookie
    session_token = request.cookies.get(settings.session_cookie_name)

    if session_token:
        # Delete session from Redis
        try:
            await SessionService.delete(session_token)
        except Exception:
            pass  # Ignore errors, we're logging out anyway

    # Clear cookie
    response.delete_cookie(
        key=settings.session_cookie_name,
        httponly=True,
        secure=not settings.debug,
        samesite="lax",
    )

    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: CurrentUser,
    db: DBSession,
):
    """
    Get current authenticated user info.
    TEMPORARY: Returns mock user when DEBUG=true (no login required).
    """
    return UserResponse.model_validate(current_user)
