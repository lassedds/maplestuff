"""
Application configuration using Pydantic Settings.
Loads from environment variables and .env file.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    # App
    app_name: str = "MapleHub OSS"
    debug: bool = False
    secret_key: str = "change-me-in-production-min-32-chars"

    # Database
    database_url: str = "postgresql://maplehub:devpassword@localhost:5432/maplehub"

    # Redis
    redis_url: str = "redis://localhost:6379"

    # Discord OAuth
    discord_client_id: str = ""
    discord_client_secret: str = ""
    discord_redirect_uri: str = "http://localhost:3000/api/auth/discord/callback"

    # URLs
    frontend_url: str = "http://localhost:3000"
    backend_url: str = "http://localhost:8000"

    @property
    def cors_origins(self) -> list[str]:
        """Allowed CORS origins."""
        origins = [self.frontend_url]
        if self.debug:
            origins.extend([
                "http://localhost:3000",
                "http://127.0.0.1:3000",
            ])
        return origins

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()
