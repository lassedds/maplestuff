"""
Discord OAuth2 client for GMSTracker.
Handles authorization flow and user info retrieval.
"""

import secrets
from dataclasses import dataclass
from urllib.parse import urlencode

import httpx

from app.config import settings


# Discord API endpoints
DISCORD_API_BASE = "https://discord.com/api/v10"
DISCORD_OAUTH_AUTHORIZE = "https://discord.com/oauth2/authorize"
DISCORD_OAUTH_TOKEN = "https://discord.com/api/oauth2/token"


@dataclass
class DiscordUser:
    """Discord user info from OAuth."""
    id: str
    username: str
    avatar: str | None
    discriminator: str | None = None  # Legacy, may be "0" for new usernames

    @property
    def avatar_url(self) -> str | None:
        """Get full avatar URL."""
        if not self.avatar:
            return None
        return f"https://cdn.discordapp.com/avatars/{self.id}/{self.avatar}.png"

    @property
    def display_name(self) -> str:
        """Get display name (handles both old and new username formats)."""
        if self.discriminator and self.discriminator != "0":
            return f"{self.username}#{self.discriminator}"
        return self.username


class DiscordOAuthError(Exception):
    """Error during Discord OAuth flow."""
    pass


class DiscordOAuthClient:
    """
    Discord OAuth2 client.

    Usage:
        client = DiscordOAuthClient()

        # Get authorization URL
        url, state = client.get_authorization_url()

        # After callback, exchange code for tokens
        tokens = await client.exchange_code(code)

        # Get user info
        user = await client.get_user_info(tokens["access_token"])
    """

    def __init__(
        self,
        client_id: str | None = None,
        client_secret: str | None = None,
        redirect_uri: str | None = None,
    ):
        self.client_id = client_id or settings.discord_client_id
        self.client_secret = client_secret or settings.discord_client_secret
        self.redirect_uri = redirect_uri or settings.discord_redirect_uri
        self.scopes = ["identify"]  # Only need basic user info

    def get_authorization_url(self, state: str | None = None) -> tuple[str, str]:
        """
        Get Discord OAuth authorization URL.

        Args:
            state: Optional state parameter for CSRF protection.
                   If not provided, a secure random state is generated.

        Returns:
            Tuple of (authorization_url, state)
        """
        if state is None:
            state = secrets.token_urlsafe(32)

        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": " ".join(self.scopes),
            "state": state,
        }

        url = f"{DISCORD_OAUTH_AUTHORIZE}?{urlencode(params)}"
        return url, state

    async def exchange_code(self, code: str) -> dict:
        """
        Exchange authorization code for access tokens.

        Args:
            code: Authorization code from callback

        Returns:
            Token response containing access_token, refresh_token, etc.

        Raises:
            DiscordOAuthError: If token exchange fails
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    DISCORD_OAUTH_TOKEN,
                    data={
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "grant_type": "authorization_code",
                        "code": code,
                        "redirect_uri": self.redirect_uri,
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                error_data = e.response.json() if e.response.content else {}
                raise DiscordOAuthError(
                    f"Token exchange failed: {error_data.get('error_description', str(e))}"
                )
            except httpx.RequestError as e:
                raise DiscordOAuthError(f"Request failed: {e}")

    async def refresh_token(self, refresh_token: str) -> dict:
        """
        Refresh an access token.

        Args:
            refresh_token: Refresh token from previous token response

        Returns:
            New token response

        Raises:
            DiscordOAuthError: If refresh fails
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    DISCORD_OAUTH_TOKEN,
                    data={
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "grant_type": "refresh_token",
                        "refresh_token": refresh_token,
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                error_data = e.response.json() if e.response.content else {}
                raise DiscordOAuthError(
                    f"Token refresh failed: {error_data.get('error_description', str(e))}"
                )
            except httpx.RequestError as e:
                raise DiscordOAuthError(f"Request failed: {e}")

    async def get_user_info(self, access_token: str) -> DiscordUser:
        """
        Get user info from Discord API.

        Args:
            access_token: Valid access token

        Returns:
            DiscordUser with user information

        Raises:
            DiscordOAuthError: If request fails
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{DISCORD_API_BASE}/users/@me",
                    headers={"Authorization": f"Bearer {access_token}"},
                )
                response.raise_for_status()
                data = response.json()

                return DiscordUser(
                    id=data["id"],
                    username=data["username"],
                    avatar=data.get("avatar"),
                    discriminator=data.get("discriminator"),
                )
            except httpx.HTTPStatusError as e:
                raise DiscordOAuthError(f"Failed to get user info: {e}")
            except httpx.RequestError as e:
                raise DiscordOAuthError(f"Request failed: {e}")

    async def revoke_token(self, token: str) -> bool:
        """
        Revoke an access or refresh token.

        Args:
            token: Token to revoke

        Returns:
            True if revocation succeeded
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{DISCORD_API_BASE}/oauth2/token/revoke",
                    data={
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "token": token,
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )
                return response.status_code == 200
            except httpx.RequestError:
                return False


# Global client instance
discord_oauth = DiscordOAuthClient()
