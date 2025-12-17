"""
Pydantic schemas for Drop Diary functionality.
"""

from datetime import datetime, date
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DiaryEntryResponse(BaseModel):
    """Single drop entry with full context."""
    model_config = ConfigDict(from_attributes=True)

    id: int  # BossRunDrop id
    boss_run_id: UUID
    item_id: int
    item_name: str | None
    quantity: int
    character_id: UUID | None = None
    character_name: str | None = None
    boss_id: int | None = None
    boss_name: str | None = None
    boss_difficulty: str | None = None
    cleared_at: datetime | None = None
    created_at: datetime


class DiaryListResponse(BaseModel):
    """Paginated list of diary entries."""
    entries: list[DiaryEntryResponse]
    total: int
    page: int
    page_size: int


class DiaryStatsResponse(BaseModel):
    """Statistics about drops."""
    total_drops: int
    unique_items: int
    unique_bosses: int
    total_quantity: int
    date_range_start: date | None = None
    date_range_end: date | None = None
    drops_by_boss: list[dict] = Field(default_factory=list)  # [{boss_id, boss_name, count}]
    drops_by_item: list[dict] = Field(default_factory=list)  # [{item_id, item_name, count}]


class DiaryTimelineEntry(BaseModel):
    """Drops grouped by date."""
    date: date
    entries: list[DiaryEntryResponse]
    total_drops: int


class DiaryTimelineResponse(BaseModel):
    """Timeline view of drops grouped by date."""
    timeline: list[DiaryTimelineEntry]
    total_entries: int


class DiaryItemResponse(BaseModel):
    """Unique item with drop count."""
    item_id: int
    item_name: str
    drop_count: int
    total_quantity: int
    first_dropped: datetime | None = None
    last_dropped: datetime | None = None

