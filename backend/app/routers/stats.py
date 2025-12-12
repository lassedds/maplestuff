"""
Community statistics API endpoints for GMSTracker.
Public read-only endpoints for aggregated drop rate data.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select, func, distinct
from sqlalchemy.orm import selectinload

from app.dependencies import DBSession
from app.models import Boss, BossRun, BossRunDrop, DropRateStats, Item, User, Character
from app.schemas import (
    DropRateStatsResponse,
    BossDropRatesResponse,
    ItemDropRatesResponse,
    CommunityStatsOverview,
    LeaderboardEntry,
    RareDropsLeaderboardResponse,
)

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/overview", response_model=CommunityStatsOverview)
async def get_community_overview(db: DBSession) -> CommunityStatsOverview:
    """
    Get an overview of community statistics.
    """
    # Total runs logged
    runs_result = await db.execute(select(func.count()).select_from(BossRun))
    total_runs = runs_result.scalar() or 0

    # Total drops logged
    drops_result = await db.execute(select(func.count()).select_from(BossRunDrop))
    total_drops = drops_result.scalar() or 0

    # Unique contributors (users who have logged at least one run)
    contributors_result = await db.execute(
        select(func.count(distinct(Character.user_id)))
        .select_from(BossRun)
        .join(Character, BossRun.character_id == Character.id)
    )
    unique_contributors = contributors_result.scalar() or 0

    # Most tracked boss
    most_tracked_result = await db.execute(
        select(Boss.name, func.count(BossRun.id).label("count"))
        .join(BossRun, Boss.id == BossRun.boss_id)
        .group_by(Boss.id, Boss.name)
        .order_by(func.count(BossRun.id).desc())
        .limit(1)
    )
    most_tracked = most_tracked_result.first()
    most_tracked_boss = most_tracked[0] if most_tracked else None

    # Most dropped item
    most_dropped_result = await db.execute(
        select(Item.name, func.count(BossRunDrop.id).label("count"))
        .join(BossRunDrop, Item.id == BossRunDrop.item_id)
        .group_by(Item.id, Item.name)
        .order_by(func.count(BossRunDrop.id).desc())
        .limit(1)
    )
    most_dropped = most_dropped_result.first()
    most_dropped_item = most_dropped[0] if most_dropped else None

    # Last updated (most recent stat computation)
    last_updated_result = await db.execute(
        select(func.max(DropRateStats.last_computed))
    )
    last_updated = last_updated_result.scalar()

    return CommunityStatsOverview(
        total_runs_logged=total_runs,
        total_drops_logged=total_drops,
        unique_contributors=unique_contributors,
        most_tracked_boss=most_tracked_boss,
        most_dropped_item=most_dropped_item,
        last_updated=last_updated,
    )


@router.get("/boss/{boss_id}", response_model=BossDropRatesResponse)
async def get_boss_drop_rates(
    boss_id: int,
    db: DBSession,
    min_sample_size: int = Query(10, ge=1, description="Minimum sample size to include"),
) -> BossDropRatesResponse:
    """
    Get drop rates for all items from a specific boss.
    Only includes stats with at least min_sample_size runs.
    """
    # Get boss
    boss_result = await db.execute(select(Boss).where(Boss.id == boss_id))
    boss = boss_result.scalar_one_or_none()
    if not boss:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Boss not found",
        )

    # Get total runs for this boss
    runs_result = await db.execute(
        select(func.count()).select_from(BossRun).where(BossRun.boss_id == boss_id)
    )
    total_runs = runs_result.scalar() or 0

    # Get drop rates from precomputed stats
    stats_result = await db.execute(
        select(DropRateStats)
        .where(
            DropRateStats.boss_id == boss_id,
            DropRateStats.sample_size >= min_sample_size,
        )
        .options(selectinload(DropRateStats.item))
        .order_by(DropRateStats.drop_rate.desc())
    )
    stats = stats_result.scalars().all()

    return BossDropRatesResponse(
        boss_id=boss.id,
        boss_name=boss.name,
        boss_difficulty=boss.difficulty,
        total_runs=total_runs,
        drops=[
            DropRateStatsResponse(
                boss_id=stat.boss_id,
                boss_name=boss.name,
                boss_difficulty=boss.difficulty,
                item_id=stat.item_id,
                item_name=stat.item.name if stat.item else None,
                item_category=stat.item.category if stat.item else None,
                item_rarity=stat.item.rarity if stat.item else None,
                sample_size=stat.sample_size,
                drop_count=stat.drop_count,
                drop_rate=stat.drop_rate,
                drop_rate_percent=stat.drop_rate * 100,
                last_computed=stat.last_computed,
            )
            for stat in stats
        ],
    )


@router.get("/item/{item_id}", response_model=ItemDropRatesResponse)
async def get_item_drop_rates(
    item_id: int,
    db: DBSession,
    min_sample_size: int = Query(10, ge=1, description="Minimum sample size to include"),
) -> ItemDropRatesResponse:
    """
    Get drop rates for a specific item from all bosses that drop it.
    """
    # Get item
    item_result = await db.execute(select(Item).where(Item.id == item_id))
    item = item_result.scalar_one_or_none()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )

    # Get drop rates from precomputed stats
    stats_result = await db.execute(
        select(DropRateStats)
        .where(
            DropRateStats.item_id == item_id,
            DropRateStats.sample_size >= min_sample_size,
        )
        .options(selectinload(DropRateStats.boss))
        .order_by(DropRateStats.drop_rate.desc())
    )
    stats = stats_result.scalars().all()

    return ItemDropRatesResponse(
        item_id=item.id,
        item_name=item.name,
        item_category=item.category,
        item_rarity=item.rarity,
        sources=[
            DropRateStatsResponse(
                boss_id=stat.boss_id,
                boss_name=stat.boss.name if stat.boss else None,
                boss_difficulty=stat.boss.difficulty if stat.boss else None,
                item_id=stat.item_id,
                item_name=item.name,
                item_category=item.category,
                item_rarity=item.rarity,
                sample_size=stat.sample_size,
                drop_count=stat.drop_count,
                drop_rate=stat.drop_rate,
                drop_rate_percent=stat.drop_rate * 100,
                last_computed=stat.last_computed,
            )
            for stat in stats
        ],
    )


@router.get("/leaderboard/rare", response_model=RareDropsLeaderboardResponse)
async def get_rare_drops_leaderboard(
    db: DBSession,
    limit: int = Query(20, ge=1, le=100),
    min_sample_size: int = Query(50, ge=10, description="Minimum sample size for accuracy"),
) -> RareDropsLeaderboardResponse:
    """
    Get a leaderboard of the rarest drops (lowest drop rates).
    Only includes items with sufficient sample size for statistical relevance.
    """
    stats_result = await db.execute(
        select(DropRateStats)
        .where(
            DropRateStats.sample_size >= min_sample_size,
            DropRateStats.drop_count > 0,  # Must have at least one drop
        )
        .options(
            selectinload(DropRateStats.boss),
            selectinload(DropRateStats.item),
        )
        .order_by(DropRateStats.drop_rate.asc())
        .limit(limit)
    )
    stats = stats_result.scalars().all()

    entries = [
        LeaderboardEntry(
            rank=i + 1,
            item_name=stat.item.name if stat.item else "Unknown",
            item_id=stat.item_id,
            boss_name=f"{stat.boss.difficulty} {stat.boss.name}" if stat.boss and stat.boss.difficulty else (stat.boss.name if stat.boss else "Unknown"),
            boss_id=stat.boss_id,
            drop_rate=stat.drop_rate,
            sample_size=stat.sample_size,
        )
        for i, stat in enumerate(stats)
    ]

    return RareDropsLeaderboardResponse(
        title="Rarest Boss Drops",
        entries=entries,
    )


@router.post("/compute", status_code=status.HTTP_202_ACCEPTED)
async def compute_drop_rates(db: DBSession) -> dict:
    """
    Recompute drop rate statistics from boss run data.
    This aggregates all BossRunDrop records to update DropRateStats.

    Note: In production, this should be a background task or scheduled job.
    """
    # Get all boss-item combinations from the drop table
    from app.models import BossDropTable

    drop_table_result = await db.execute(select(BossDropTable))
    drop_table_entries = drop_table_result.scalars().all()

    updated_count = 0
    for entry in drop_table_entries:
        # Count total runs for this boss
        runs_result = await db.execute(
            select(func.count())
            .select_from(BossRun)
            .where(BossRun.boss_id == entry.boss_id, BossRun.is_clear == True)
        )
        sample_size = runs_result.scalar() or 0

        # Count drops of this item from this boss
        drops_result = await db.execute(
            select(func.count())
            .select_from(BossRunDrop)
            .join(BossRun, BossRunDrop.boss_run_id == BossRun.id)
            .where(
                BossRun.boss_id == entry.boss_id,
                BossRunDrop.item_id == entry.item_id,
            )
        )
        drop_count = drops_result.scalar() or 0

        # Compute drop rate
        drop_rate = drop_count / sample_size if sample_size > 0 else 0.0

        # Upsert stats
        existing_result = await db.execute(
            select(DropRateStats).where(
                DropRateStats.boss_id == entry.boss_id,
                DropRateStats.item_id == entry.item_id,
            )
        )
        existing = existing_result.scalar_one_or_none()

        if existing:
            existing.sample_size = sample_size
            existing.drop_count = drop_count
            existing.drop_rate = drop_rate
            existing.last_computed = datetime.now(timezone.utc)
        else:
            new_stat = DropRateStats(
                boss_id=entry.boss_id,
                item_id=entry.item_id,
                sample_size=sample_size,
                drop_count=drop_count,
                drop_rate=drop_rate,
            )
            db.add(new_stat)

        updated_count += 1

    await db.commit()

    return {
        "status": "completed",
        "stats_updated": updated_count,
        "computed_at": datetime.now(timezone.utc).isoformat(),
    }
