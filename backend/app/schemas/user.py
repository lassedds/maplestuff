"""
Pydantic schemas for User and UserSettings.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    """Base user fields."""
    discord_username: str | None = None
    discord_avatar: str | None = None


class UserCreate(BaseModel):
    """Fields for creating a user (from Discord OAuth)."""
    discord_id: str
    discord_username: str | None = None
    discord_avatar: str | None = None


class UserUpdate(BaseModel):
    """Fields that can be updated on a user."""
    discord_username: str | None = None
    discord_avatar: str | None = None


class UserResponse(UserBase):
    """User response schema."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    discord_id: str
    created_at: datetime
    updated_at: datetime


class UserSettingsBase(BaseModel):
    """Base user settings fields."""
    timezone: str = "UTC"
    theme: str = "dark"
    default_world: str | None = None


class UserSettingsCreate(UserSettingsBase):
    """Fields for creating user settings."""
    pass


class UserSettingsUpdate(BaseModel):
    """Fields that can be updated on user settings."""
    timezone: str | None = None
    theme: str | None = None
    default_world: str | None = None
    settings_json: dict | None = None


class UserSettingsResponse(UserSettingsBase):
    """User settings response schema."""
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    settings_json: dict
    created_at: datetime
    updated_at: datetime
