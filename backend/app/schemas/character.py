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
    nexon_ocid: str | None = None
    character_icon_url: str | None = None
    created_at: datetime
    updated_at: datetime


class CharacterLookupRequest(BaseModel):
    """Request schema for looking up character data from Nexon API."""
    character_name: str = Field(..., min_length=1, max_length=255)
    world: str = Field(..., min_length=1, max_length=100)


class CharacterLookupResponse(BaseModel):
    """Response schema for character lookup (before creating).
    Matches the Nexon Rankings API response format.
    """
    character_name: str
    world: str  # Mapped from worldID
    level: int | None = None
    job: str | None = None  # From jobName
    character_image: str | None = None  # From characterImgURL
    character_icon_url: str | None = None  # From characterImgURL
    nexon_ocid: str | None = None  # From characterID (if not 0)


class CharacterListResponse(BaseModel):
    """List of characters response."""
    characters: list[CharacterResponse]
    total: int
