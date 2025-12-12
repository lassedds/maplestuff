"""
Pydantic schemas for Character.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CharacterBase(BaseModel):
    """Base character fields."""
    character_name: str = Field(..., min_length=1, max_length=255)
    world: str = Field(..., min_length=1, max_length=100)
    job: str | None = Field(None, max_length=100)
    level: int | None = Field(None, ge=1, le=300)
    is_main: bool = False


class CharacterCreate(CharacterBase):
    """Fields for creating a character."""
    pass


class CharacterUpdate(BaseModel):
    """Fields that can be updated on a character."""
    job: str | None = None
    level: int | None = Field(None, ge=1, le=300)
    is_main: bool | None = None


class CharacterResponse(CharacterBase):
    """Character response schema."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime


class CharacterListResponse(BaseModel):
    """List of characters response."""
    characters: list[CharacterResponse]
    total: int
