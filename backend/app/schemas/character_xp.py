"""
Schemas for Character XP tracking API.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class CharacterXPSnapshotCreate(BaseModel):
    """Schema for creating an XP snapshot."""
    
    character_id: UUID
    snapshot_date: date
    total_xp: Decimal
    level: Optional[int] = None


class CharacterXPSnapshot(BaseModel):
    """Schema for XP snapshot response."""
    
    id: UUID
    character_id: UUID
    snapshot_date: date
    total_xp: Decimal
    level: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CharacterXPSnapshotListResponse(BaseModel):
    """Schema for XP snapshot list response."""
    
    snapshots: list[CharacterXPSnapshot]
    total: int


class CharacterXPDailyGain(BaseModel):
    """Schema for daily XP gain calculation."""
    
    date: date
    xp_gained: Decimal
    level: Optional[int] = None


class CharacterXPHistoryResponse(BaseModel):
    """Schema for character XP history with daily gains."""
    
    character_id: UUID
    character_name: str
    daily_gains: list[CharacterXPDailyGain]
    total_days: int
    average_daily_xp: Decimal
    total_xp_gained: Decimal


class CharacterXPOverview(BaseModel):
    """Schema for character XP overview in the list."""
    
    character_id: UUID
    character_name: str
    world: str
    job: Optional[str] = None
    level: Optional[int] = None
    character_icon_url: Optional[str] = None
    current_xp: Optional[Decimal] = None
    xp_today: Optional[Decimal] = None
    xp_yesterday: Optional[Decimal] = None
    average_xp: Optional[Decimal] = None
    total_xp_gained: Optional[Decimal] = None
    progress_percent: Optional[Decimal] = None
    days_tracked: int


class CharacterXPOverviewListResponse(BaseModel):
    """Schema for character XP overview list."""
    
    characters: list[CharacterXPOverview]
