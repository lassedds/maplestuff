"""
Schemas for XP Entry API.
"""

from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class XPEntryCreate(BaseModel):
    """Schema for creating an XP entry."""
    
    entry_date: date
    level: int = Field(ge=200, le=299)
    old_percent: Decimal = Field(ge=0, le=100, decimal_places=2)
    new_percent: Decimal = Field(ge=0, le=100, decimal_places=2)
    epic_dungeon: bool = False
    epic_dungeon_multiplier: int = Field(default=1, ge=1, le=9)


class XPEntryUpdate(BaseModel):
    """Schema for updating an XP entry."""
    
    level: Optional[int] = Field(None, ge=200, le=299)
    old_percent: Optional[Decimal] = Field(None, ge=0, le=100, decimal_places=2)
    new_percent: Optional[Decimal] = Field(None, ge=0, le=100, decimal_places=2)
    epic_dungeon: Optional[bool] = None
    epic_dungeon_multiplier: Optional[int] = Field(None, ge=1, le=9)


class XPEntry(BaseModel):
    """Schema for XP entry response."""
    
    id: UUID
    user_id: UUID
    entry_date: date
    level: int
    old_percent: Decimal
    new_percent: Decimal
    xp_gained_trillions: Decimal
    xp_gained_billions: Decimal
    epic_dungeon: bool
    epic_dungeon_xp_trillions: Optional[Decimal] = None
    epic_dungeon_xp_billions: Optional[Decimal] = None
    epic_dungeon_multiplier: int
    total_daily_xp_trillions: Decimal
    total_daily_xp_billions: Decimal
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


class XPEntryListResponse(BaseModel):
    """Schema for XP entry list response."""
    
    entries: list[XPEntry]
    total: int


class XPStats(BaseModel):
    """Schema for XP statistics."""
    
    seven_day_average_trillions: Decimal
    seven_day_average_billions: Decimal
    total_xp_trillions: Decimal
    total_xp_billions: Decimal
    entry_count: int
