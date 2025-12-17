"""
Drop Diary API endpoints.
Provides filtered views of user's drop history with statistics.
"""

from datetime import datetime, date
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from app.dependencies import DBSession, CurrentUser
from app.models.character import Character
from app.models.boss_run import BossRun, BossRunDrop
from app.models.boss import Boss
from app.models.item import Item
from app.schemas.diary import (
    DiaryEntryResponse,
    DiaryListResponse,
    DiaryStatsResponse,
    DiaryTimelineResponse,
    DiaryTimelineEntry,
    DiaryItemResponse,
)

router = APIRouter(prefix="/diary", tags=["diary"])


@router.get("", response_model=DiaryListResponse)
async def list_diary_entries(
    db: DBSession,
    current_user: CurrentUser,
    character_id: UUID | None = Query(None, description="Filter by character"),
    boss_id: int | None = Query(None, description="Filter by boss"),
    item_id: int | None = Query(None, description="Filter by item"),
    start_date: date | None = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: date | None = Query(None, description="End date (YYYY-MM-DD)"),
    search: str | None = Query(None, description="Search item names"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    include_community: bool = Query(False, description="Include community-wide statistics (future feature)"),
) -> DiaryListResponse:
    """
    List all drop entries for the current user with filters.
    
    Note: include_community parameter is reserved for future community-wide statistics.
    When enabled, it will aggregate data from all users for community drop rate analysis.
    """
    # Get user's character IDs
    char_query = select(Character.id).where(Character.user_id == current_user.id)
    if character_id:
        char_query = char_query.where(Character.id == character_id)
    
    char_result = await db.execute(char_query)
    character_ids = [r[0] for r in char_result.all()]

    # TODO: When include_community=True, expand to all users' characters for community statistics
    # For now, this parameter is ignored and only user's own data is returned
    
    if not character_ids:
        return DiaryListResponse(entries=[], total=0, page=page, page_size=page_size)

    # Build query for boss runs
    run_query = select(BossRun).where(BossRun.character_id.in_(character_ids))
    
    if boss_id:
        run_query = run_query.where(BossRun.boss_id == boss_id)
    
    if start_date:
        run_query = run_query.where(BossRun.cleared_at >= datetime.combine(start_date, datetime.min.time()))
    
    if end_date:
        run_query = run_query.where(BossRun.cleared_at <= datetime.combine(end_date, datetime.max.time()))

    # Get boss run IDs
    run_result = await db.execute(run_query)
    run_ids = [run.id for run in run_result.scalars().all()]

    if not run_ids:
        return DiaryListResponse(entries=[], total=0, page=page, page_size=page_size)

    # Build query for drops - join BossRun for ordering
    drop_query = (
        select(BossRunDrop)
        .join(BossRun, BossRunDrop.boss_run_id == BossRun.id)
        .where(BossRunDrop.boss_run_id.in_(run_ids))
        .options(
            selectinload(BossRunDrop.boss_run).selectinload(BossRun.character),
            selectinload(BossRunDrop.boss_run).selectinload(BossRun.boss),
            selectinload(BossRunDrop.item),
        )
    )

    if item_id:
        drop_query = drop_query.where(BossRunDrop.item_id == item_id)

    if search:
        # Search in item names
        item_subquery = select(Item.id).where(Item.name.ilike(f"%{search}%"))
        drop_query = drop_query.where(BossRunDrop.item_id.in_(item_subquery))

    # Count total (before pagination)
    count_query = select(func.count()).select_from(drop_query.subquery())
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    # Paginate - order by boss_run cleared_at or created_at
    drop_query = (
        drop_query
        .order_by(BossRun.cleared_at.desc(), BossRun.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    result = await db.execute(drop_query)
    drops = result.scalars().all()

    entries = []
    for drop in drops:
        boss_run = drop.boss_run
        entries.append(
            DiaryEntryResponse(
                id=drop.id,
                boss_run_id=drop.boss_run_id,
                item_id=drop.item_id,
                item_name=drop.item.name if drop.item else None,
                quantity=drop.quantity,
                character_id=boss_run.character_id if boss_run else None,
                character_name=boss_run.character.character_name if boss_run and boss_run.character else None,
                boss_id=boss_run.boss_id if boss_run else None,
                boss_name=boss_run.boss.name if boss_run and boss_run.boss else None,
                boss_difficulty=boss_run.boss.difficulty if boss_run and boss_run.boss else None,
                cleared_at=boss_run.cleared_at if boss_run else None,
                created_at=boss_run.created_at if boss_run else None,
            )
        )

    return DiaryListResponse(entries=entries, total=total, page=page, page_size=page_size)


@router.get("/stats", response_model=DiaryStatsResponse)
async def get_diary_stats(
    db: DBSession,
    current_user: CurrentUser,
    character_id: UUID | None = Query(None, description="Filter by character"),
    boss_id: int | None = Query(None, description="Filter by boss"),
    item_id: int | None = Query(None, description="Filter by item"),
    start_date: date | None = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: date | None = Query(None, description="End date (YYYY-MM-DD)"),
    include_community: bool = Query(False, description="Include community-wide statistics (future feature)"),
) -> DiaryStatsResponse:
    """
    Get statistics about drops.
    
    Note: include_community parameter is reserved for future community-wide statistics.
    When enabled, it will aggregate data from all users for community drop rate analysis.
    """
    # Get user's character IDs
    char_query = select(Character.id).where(Character.user_id == current_user.id)
    if character_id:
        char_query = char_query.where(Character.id == character_id)
    
    char_result = await db.execute(char_query)
    character_ids = [r[0] for r in char_result.all()]

    # TODO: When include_community=True, expand to all users' characters for community statistics
    # For now, this parameter is ignored and only user's own data is returned

    if not character_ids:
        return DiaryStatsResponse(
            total_drops=0,
            unique_items=0,
            unique_bosses=0,
            total_quantity=0,
        )

    # Build query for boss runs
    run_query = select(BossRun).where(BossRun.character_id.in_(character_ids))
    
    if boss_id:
        run_query = run_query.where(BossRun.boss_id == boss_id)
    
    if start_date:
        run_query = run_query.where(BossRun.cleared_at >= datetime.combine(start_date, datetime.min.time()))
    
    if end_date:
        run_query = run_query.where(BossRun.cleared_at <= datetime.combine(end_date, datetime.max.time()))

    run_result = await db.execute(run_query)
    run_ids = [run.id for run in run_result.scalars().all()]

    if not run_ids:
        return DiaryStatsResponse(
            total_drops=0,
            unique_items=0,
            unique_bosses=0,
            total_quantity=0,
        )

    # Build query for drops
    drop_query = select(BossRunDrop).where(BossRunDrop.boss_run_id.in_(run_ids))
    
    if item_id:
        drop_query = drop_query.where(BossRunDrop.item_id == item_id)

    # Get all drops
    drop_result = await db.execute(
        drop_query.options(
            selectinload(BossRunDrop.boss_run).selectinload(BossRun.boss),
            selectinload(BossRunDrop.item),
        )
    )
    drops = drop_result.scalars().all()

    # Calculate statistics
    total_drops = len(drops)
    unique_items = len(set(drop.item_id for drop in drops))
    unique_bosses = len(set(drop.boss_run.boss_id for drop in drops if drop.boss_run))
    total_quantity = sum(drop.quantity for drop in drops)

    # Drops by boss
    boss_counts: dict[int, dict] = {}
    for drop in drops:
        if drop.boss_run and drop.boss_run.boss:
            boss_id = drop.boss_run.boss_id
            if boss_id not in boss_counts:
                boss_counts[boss_id] = {
                    "boss_id": boss_id,
                    "boss_name": drop.boss_run.boss.name,
                    "count": 0,
                }
            boss_counts[boss_id]["count"] += drop.quantity

    # Drops by item
    item_counts: dict[int, dict] = {}
    for drop in drops:
        item_id = drop.item_id
        if item_id not in item_counts:
            item_counts[item_id] = {
                "item_id": item_id,
                "item_name": drop.item.name if drop.item else f"Item {item_id}",
                "count": 0,
            }
        item_counts[item_id]["count"] += drop.quantity

    return DiaryStatsResponse(
        total_drops=total_drops,
        unique_items=unique_items,
        unique_bosses=unique_bosses,
        total_quantity=total_quantity,
        date_range_start=start_date,
        date_range_end=end_date,
        drops_by_boss=sorted(boss_counts.values(), key=lambda x: x["count"], reverse=True),
        drops_by_item=sorted(item_counts.values(), key=lambda x: x["count"], reverse=True),
    )


@router.get("/items", response_model=list[DiaryItemResponse])
async def get_diary_items(
    db: DBSession,
    current_user: CurrentUser,
    character_id: UUID | None = Query(None, description="Filter by character"),
    boss_id: int | None = Query(None, description="Filter by boss"),
    start_date: date | None = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: date | None = Query(None, description="End date (YYYY-MM-DD)"),
    include_community: bool = Query(False, description="Include community-wide statistics (future feature)"),
) -> list[DiaryItemResponse]:
    """
    Get unique items that have been dropped with drop counts.
    
    Note: include_community parameter is reserved for future community-wide statistics.
    When enabled, it will aggregate data from all users for community drop rate analysis.
    """
    # Get user's character IDs
    char_query = select(Character.id).where(Character.user_id == current_user.id)
    if character_id:
        char_query = char_query.where(Character.id == character_id)
    
    char_result = await db.execute(char_query)
    character_ids = [r[0] for r in char_result.all()]

    # TODO: When include_community=True, expand to all users' characters for community statistics
    # For now, this parameter is ignored and only user's own data is returned

    if not character_ids:
        return []

    # Build query for boss runs
    run_query = select(BossRun).where(BossRun.character_id.in_(character_ids))
    
    if boss_id:
        run_query = run_query.where(BossRun.boss_id == boss_id)
    
    if start_date:
        run_query = run_query.where(BossRun.cleared_at >= datetime.combine(start_date, datetime.min.time()))
    
    if end_date:
        run_query = run_query.where(BossRun.cleared_at <= datetime.combine(end_date, datetime.max.time()))

    run_result = await db.execute(run_query)
    run_ids = [run.id for run in run_result.scalars().all()]

    if not run_ids:
        return []

    # Get drops grouped by item
    drop_result = await db.execute(
        select(BossRunDrop)
        .where(BossRunDrop.boss_run_id.in_(run_ids))
        .options(
            selectinload(BossRunDrop.item),
        )
    )
    drops = drop_result.scalars().all()

    # Group by item
    item_data: dict[int, dict] = {}
    for drop in drops:
        item_id = drop.item_id
        if item_id not in item_data:
            item_data[item_id] = {
                "item_id": item_id,
                "item_name": drop.item.name if drop.item else f"Item {item_id}",
                "drop_count": 0,
                "total_quantity": 0,
                "first_dropped": drop.created_at,
                "last_dropped": drop.created_at,
            }
        item_data[item_id]["drop_count"] += 1
        item_data[item_id]["total_quantity"] += drop.quantity
        if drop.created_at < item_data[item_id]["first_dropped"]:
            drop_time = drop.boss_run.created_at if drop.boss_run else None
        if drop_time:
            if item_data[item_id]["first_dropped"] is None or drop_time < item_data[item_id]["first_dropped"]:
                item_data[item_id]["first_dropped"] = drop_time
            if item_data[item_id]["last_dropped"] is None or drop_time > item_data[item_id]["last_dropped"]:
                item_data[item_id]["last_dropped"] = drop_time

    return [
        DiaryItemResponse(**data)
        for data in sorted(item_data.values(), key=lambda x: x["total_quantity"], reverse=True)
    ]


@router.get("/timeline", response_model=DiaryTimelineResponse)
async def get_diary_timeline(
    db: DBSession,
    current_user: CurrentUser,
    character_id: UUID | None = Query(None, description="Filter by character"),
    boss_id: int | None = Query(None, description="Filter by boss"),
    item_id: int | None = Query(None, description="Filter by item"),
    start_date: date | None = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: date | None = Query(None, description="End date (YYYY-MM-DD)"),
    include_community: bool = Query(False, description="Include community-wide statistics (future feature)"),
) -> DiaryTimelineResponse:
    """
    Get drops grouped by date (timeline view).
    
    Note: include_community parameter is reserved for future community-wide statistics.
    When enabled, it will aggregate data from all users for community drop rate analysis.
    """
    # Get user's character IDs
    char_query = select(Character.id).where(Character.user_id == current_user.id)
    if character_id:
        char_query = char_query.where(Character.id == character_id)
    
    char_result = await db.execute(char_query)
    character_ids = [r[0] for r in char_result.all()]

    # TODO: When include_community=True, expand to all users' characters for community statistics
    # For now, this parameter is ignored and only user's own data is returned

    if not character_ids:
        return DiaryTimelineResponse(timeline=[], total_entries=0)

    # Build query for boss runs
    run_query = select(BossRun).where(BossRun.character_id.in_(character_ids))
    
    if boss_id:
        run_query = run_query.where(BossRun.boss_id == boss_id)
    
    if start_date:
        run_query = run_query.where(BossRun.cleared_at >= datetime.combine(start_date, datetime.min.time()))
    
    if end_date:
        run_query = run_query.where(BossRun.cleared_at <= datetime.combine(end_date, datetime.max.time()))

    run_result = await db.execute(run_query)
    run_ids = [run.id for run in run_result.scalars().all()]

    if not run_ids:
        return DiaryTimelineResponse(timeline=[], total_entries=0)

    # Get all drops
    drop_query = (
        select(BossRunDrop)
        .where(BossRunDrop.boss_run_id.in_(run_ids))
        .options(
            selectinload(BossRunDrop.boss_run).selectinload(BossRun.character),
            selectinload(BossRunDrop.boss_run).selectinload(BossRun.boss),
            selectinload(BossRunDrop.item),
        )
    )

    if item_id:
        drop_query = drop_query.where(BossRunDrop.item_id == item_id)

    # Join BossRun for ordering
    drop_query = (
        drop_query
        .join(BossRun, BossRunDrop.boss_run_id == BossRun.id)
        .order_by(BossRun.cleared_at.desc(), BossRun.created_at.desc())
    )
    # Re-add selectinload after join
    drop_query = drop_query.options(
        selectinload(BossRunDrop.boss_run).selectinload(BossRun.character),
        selectinload(BossRunDrop.boss_run).selectinload(BossRun.boss),
        selectinload(BossRunDrop.item),
    )
    drop_result = await db.execute(drop_query)
    drops = drop_result.scalars().all()

    # Group by date (use boss_run cleared_at or created_at)
    timeline_dict: dict[date, list[BossRunDrop]] = {}
    for drop in drops:
        if drop.boss_run:
            drop_date = (drop.boss_run.cleared_at or drop.boss_run.created_at).date()
            if drop_date not in timeline_dict:
                timeline_dict[drop_date] = []
            timeline_dict[drop_date].append(drop)

    # Convert to timeline entries
    timeline = []
    for drop_date in sorted(timeline_dict.keys(), reverse=True):
        date_drops = timeline_dict[drop_date]
        entries = []
        for drop in date_drops:
            boss_run = drop.boss_run
            entries.append(
                DiaryEntryResponse(
                    id=drop.id,
                    boss_run_id=drop.boss_run_id,
                    item_id=drop.item_id,
                    item_name=drop.item.name if drop.item else None,
                    quantity=drop.quantity,
                    character_id=boss_run.character_id if boss_run else None,
                    character_name=boss_run.character.character_name if boss_run and boss_run.character else None,
                    boss_id=boss_run.boss_id if boss_run else None,
                    boss_name=boss_run.boss.name if boss_run and boss_run.boss else None,
                    boss_difficulty=boss_run.boss.difficulty if boss_run and boss_run.boss else None,
                    cleared_at=boss_run.cleared_at if boss_run else None,
                    created_at=drop.created_at,
                )
            )
        
        timeline.append(
            DiaryTimelineEntry(
                date=drop_date,
                entries=entries,
                total_drops=len(entries),
            )
        )

    return DiaryTimelineResponse(
        timeline=timeline,
        total_entries=len(drops),
    )


# TODO: Future endpoints for editing/deleting diary entries
# These will be implemented when needed for user management of their drop history
#
# @router.put("/entries/{entry_id}", response_model=DiaryEntryResponse)
# async def update_diary_entry(
#     entry_id: int,
#     db: DBSession,
#     current_user: CurrentUser,
#     # Update fields like quantity, notes, etc.
# ) -> DiaryEntryResponse:
#     """
#     Update a diary entry (e.g., correct quantity, add notes).
#     """
#     pass
#
# @router.delete("/entries/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_diary_entry(
#     entry_id: int,
#     db: DBSession,
#     current_user: CurrentUser,
# ) -> None:
#     """
#     Delete a diary entry.
#     """
#     pass

