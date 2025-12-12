"""
Pydantic schemas for boss run tracking.
Includes weekly reset calculation for GMS (Thursday 00:00 UTC).
"""

from datetime import datetime, date, timedelta, timezone
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


def get_current_week_start() -> date:
    """
    Get the start of the current weekly reset period.
    GMS resets on Thursday 00:00 UTC.
    Returns the most recent Thursday (or today if Thursday).
    """
    now = datetime.now(timezone.utc)
    # Monday = 0, Thursday = 3
    days_since_thursday = (now.weekday() - 3) % 7
    week_start = now.date() - timedelta(days=days_since_thursday)
    return week_start


def get_week_start_for_date(dt: datetime | date) -> date:
    """
    Get the week start (Thursday) for a given date.
    """
    if isinstance(dt, datetime):
        dt = dt.date()
    days_since_thursday = (dt.weekday() - 3) % 7
    return dt - timedelta(days=days_since_thursday)


# Request schemas
class BossRunCreate(BaseModel):
    """Schema for creating a new boss run."""

    boss_id: int = Field(..., description="ID of the boss that was cleared")
    character_id: UUID = Field(..., description="ID of the character that cleared the boss")
    cleared_at: datetime | None = Field(
        None,
        description="When the boss was cleared (defaults to now)",
    )
    party_size: int = Field(1, ge=1, le=6, description="Party size at time of clear")
    notes: str | None = Field(None, max_length=500)
    is_clear: bool = Field(True, description="Whether this was a successful clear")
    drop_item_ids: list[int] = Field(
        default_factory=list,
        description="IDs of items that dropped",
    )


class BossRunUpdate(BaseModel):
    """Schema for updating a boss run."""

    party_size: int | None = Field(None, ge=1, le=6)
    notes: str | None = Field(None, max_length=500)
    is_clear: bool | None = None


class BossRunDropCreate(BaseModel):
    """Schema for adding a drop to a boss run."""

    item_id: int = Field(..., description="ID of the item that dropped")
    quantity: int = Field(1, ge=1)


# Response schemas
class BossRunDropResponse(BaseModel):
    """Response schema for a boss run drop."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    item_id: int
    item_name: str | None = None
    quantity: int


class BossRunResponse(BaseModel):
    """Response schema for a boss run."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    character_id: UUID
    boss_id: int
    cleared_at: datetime
    week_start: date
    party_size: int
    notes: str | None
    is_clear: bool
    created_at: datetime


class BossRunWithDetailsResponse(BossRunResponse):
    """Response schema for a boss run with character and boss details."""

    character_name: str | None = None
    boss_name: str | None = None
    boss_difficulty: str | None = None
    drops: list[BossRunDropResponse] = []


class WeeklyBossProgressResponse(BaseModel):
    """Response showing boss clear status for the current week."""

    boss_id: int
    boss_name: str
    boss_difficulty: str | None
    reset_type: str
    crystal_meso: int | None
    cleared: bool
    cleared_at: datetime | None = None
    character_id: UUID | None = None
    character_name: str | None = None


class WeeklySummaryResponse(BaseModel):
    """Summary of weekly boss progress."""

    week_start: date
    week_end: date
    total_bosses: int
    cleared_count: int
    total_meso: int
    progress: list[WeeklyBossProgressResponse]


class BossRunListResponse(BaseModel):
    """Paginated list of boss runs."""

    runs: list[BossRunWithDetailsResponse]
    total: int
    page: int
    page_size: int
