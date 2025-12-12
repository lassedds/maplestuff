"""
Pydantic schemas for community drop rate statistics.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DropRateStatsResponse(BaseModel):
    """Response schema for a single drop rate statistic."""

    model_config = ConfigDict(from_attributes=True)

    boss_id: int
    boss_name: str | None = None
    boss_difficulty: str | None = None
    item_id: int
    item_name: str | None = None
    item_category: str | None = None
    item_rarity: str | None = None
    sample_size: int
    drop_count: int
    drop_rate: float
    drop_rate_percent: float | None = None  # Computed as drop_rate * 100
    last_computed: datetime


class BossDropRatesResponse(BaseModel):
    """Drop rates for all items from a specific boss."""

    boss_id: int
    boss_name: str
    boss_difficulty: str | None
    total_runs: int
    drops: list[DropRateStatsResponse]


class ItemDropRatesResponse(BaseModel):
    """Drop rates for a specific item from all bosses."""

    item_id: int
    item_name: str
    item_category: str | None
    item_rarity: str | None
    sources: list[DropRateStatsResponse]


class CommunityStatsOverview(BaseModel):
    """Overview of community statistics."""

    total_runs_logged: int
    total_drops_logged: int
    unique_contributors: int
    most_tracked_boss: str | None = None
    most_dropped_item: str | None = None
    last_updated: datetime | None = None


class LeaderboardEntry(BaseModel):
    """Entry for a drop leaderboard."""

    rank: int
    item_name: str
    item_id: int
    boss_name: str
    boss_id: int
    drop_rate: float
    sample_size: int


class RareDropsLeaderboardResponse(BaseModel):
    """Leaderboard of rarest drops."""

    title: str
    entries: list[LeaderboardEntry]
