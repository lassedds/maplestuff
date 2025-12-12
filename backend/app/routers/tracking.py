"""
Boss tracking API endpoints for GMSTracker.
Authenticated endpoints for logging and viewing boss clears.
"""

from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload

from app.dependencies import DBSession, CurrentUser
from app.models import Boss, BossRun, BossRunDrop, Character, Item
from app.schemas import (
    BossRunCreate,
    BossRunUpdate,
    BossRunDropCreate,
    BossRunResponse,
    BossRunWithDetailsResponse,
    BossRunDropResponse,
    WeeklyBossProgressResponse,
    WeeklySummaryResponse,
    BossRunListResponse,
    get_current_week_start,
    get_week_start_for_date,
)

router = APIRouter(prefix="/tracking", tags=["tracking"])


@router.post("/runs", response_model=BossRunWithDetailsResponse, status_code=status.HTTP_201_CREATED)
async def create_boss_run(
    run_data: BossRunCreate,
    db: DBSession,
    current_user: CurrentUser,
) -> BossRunWithDetailsResponse:
    """
    Log a boss clear for a character.
    The character must belong to the current user.
    """
    # Verify character belongs to user
    result = await db.execute(
        select(Character).where(
            Character.id == run_data.character_id,
            Character.user_id == current_user.id,
        )
    )
    character = result.scalar_one_or_none()
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found or does not belong to you",
        )

    # Verify boss exists
    result = await db.execute(select(Boss).where(Boss.id == run_data.boss_id))
    boss = result.scalar_one_or_none()
    if not boss:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Boss not found",
        )

    # Use provided timestamp or current time
    cleared_at = run_data.cleared_at or datetime.now(timezone.utc)
    week_start = get_week_start_for_date(cleared_at)

    # Check if already cleared this week (for weekly bosses)
    if boss.reset_type == "weekly":
        existing = await db.execute(
            select(BossRun).where(
                BossRun.character_id == run_data.character_id,
                BossRun.boss_id == run_data.boss_id,
                BossRun.week_start == week_start,
                BossRun.is_clear == True,
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This boss has already been cleared this week on this character",
            )

    # Create boss run
    boss_run = BossRun(
        character_id=run_data.character_id,
        boss_id=run_data.boss_id,
        cleared_at=cleared_at,
        week_start=week_start,
        party_size=run_data.party_size,
        notes=run_data.notes,
        is_clear=run_data.is_clear,
    )
    db.add(boss_run)
    await db.flush()

    # Add drops if provided
    for item_id in run_data.drop_item_ids:
        # Verify item exists
        item_result = await db.execute(select(Item).where(Item.id == item_id))
        if item_result.scalar_one_or_none():
            drop = BossRunDrop(boss_run_id=boss_run.id, item_id=item_id, quantity=1)
            db.add(drop)

    await db.commit()
    await db.refresh(boss_run)

    # Load relationships
    result = await db.execute(
        select(BossRun)
        .where(BossRun.id == boss_run.id)
        .options(
            selectinload(BossRun.character),
            selectinload(BossRun.boss),
            selectinload(BossRun.drops).selectinload(BossRunDrop.item),
        )
    )
    boss_run = result.scalar_one()

    return BossRunWithDetailsResponse(
        id=boss_run.id,
        character_id=boss_run.character_id,
        boss_id=boss_run.boss_id,
        cleared_at=boss_run.cleared_at,
        week_start=boss_run.week_start,
        party_size=boss_run.party_size,
        notes=boss_run.notes,
        is_clear=boss_run.is_clear,
        created_at=boss_run.created_at,
        character_name=boss_run.character.character_name,
        boss_name=boss_run.boss.name,
        boss_difficulty=boss_run.boss.difficulty,
        drops=[
            BossRunDropResponse(
                id=drop.id,
                item_id=drop.item_id,
                item_name=drop.item.name if drop.item else None,
                quantity=drop.quantity,
            )
            for drop in boss_run.drops
        ],
    )


@router.get("/runs", response_model=BossRunListResponse)
async def list_boss_runs(
    db: DBSession,
    current_user: CurrentUser,
    character_id: UUID | None = Query(None, description="Filter by character"),
    boss_id: int | None = Query(None, description="Filter by boss"),
    week_start: str | None = Query(None, description="Filter by week (YYYY-MM-DD)"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> BossRunListResponse:
    """
    List boss runs for the current user's characters.
    """
    # Get user's character IDs
    char_result = await db.execute(
        select(Character.id).where(Character.user_id == current_user.id)
    )
    character_ids = [r[0] for r in char_result.all()]

    if not character_ids:
        return BossRunListResponse(runs=[], total=0, page=page, page_size=page_size)

    # Build query
    query = select(BossRun).where(BossRun.character_id.in_(character_ids))

    if character_id:
        if character_id not in character_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Character does not belong to you",
            )
        query = query.where(BossRun.character_id == character_id)

    if boss_id:
        query = query.where(BossRun.boss_id == boss_id)

    if week_start:
        from datetime import date as date_type
        try:
            week_date = date_type.fromisoformat(week_start)
            query = query.where(BossRun.week_start == week_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid week_start format. Use YYYY-MM-DD",
            )

    # Count total
    count_result = await db.execute(
        select(func.count()).select_from(query.subquery())
    )
    total = count_result.scalar() or 0

    # Paginate and load relationships
    query = (
        query
        .options(
            selectinload(BossRun.character),
            selectinload(BossRun.boss),
            selectinload(BossRun.drops).selectinload(BossRunDrop.item),
        )
        .order_by(BossRun.cleared_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    result = await db.execute(query)
    runs = result.scalars().all()

    return BossRunListResponse(
        runs=[
            BossRunWithDetailsResponse(
                id=run.id,
                character_id=run.character_id,
                boss_id=run.boss_id,
                cleared_at=run.cleared_at,
                week_start=run.week_start,
                party_size=run.party_size,
                notes=run.notes,
                is_clear=run.is_clear,
                created_at=run.created_at,
                character_name=run.character.character_name,
                boss_name=run.boss.name,
                boss_difficulty=run.boss.difficulty,
                drops=[
                    BossRunDropResponse(
                        id=drop.id,
                        item_id=drop.item_id,
                        item_name=drop.item.name if drop.item else None,
                        quantity=drop.quantity,
                    )
                    for drop in run.drops
                ],
            )
            for run in runs
        ],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/runs/{run_id}", response_model=BossRunWithDetailsResponse)
async def get_boss_run(
    run_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
) -> BossRunWithDetailsResponse:
    """Get a specific boss run."""
    result = await db.execute(
        select(BossRun)
        .where(BossRun.id == run_id)
        .options(
            selectinload(BossRun.character),
            selectinload(BossRun.boss),
            selectinload(BossRun.drops).selectinload(BossRunDrop.item),
        )
    )
    run = result.scalar_one_or_none()

    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Boss run not found",
        )

    # Verify ownership
    if run.character.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Boss run does not belong to you",
        )

    return BossRunWithDetailsResponse(
        id=run.id,
        character_id=run.character_id,
        boss_id=run.boss_id,
        cleared_at=run.cleared_at,
        week_start=run.week_start,
        party_size=run.party_size,
        notes=run.notes,
        is_clear=run.is_clear,
        created_at=run.created_at,
        character_name=run.character.character_name,
        boss_name=run.boss.name,
        boss_difficulty=run.boss.difficulty,
        drops=[
            BossRunDropResponse(
                id=drop.id,
                item_id=drop.item_id,
                item_name=drop.item.name if drop.item else None,
                quantity=drop.quantity,
            )
            for drop in run.drops
        ],
    )


@router.delete("/runs/{run_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_boss_run(
    run_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
) -> None:
    """Delete a boss run."""
    result = await db.execute(
        select(BossRun)
        .where(BossRun.id == run_id)
        .options(selectinload(BossRun.character))
    )
    run = result.scalar_one_or_none()

    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Boss run not found",
        )

    if run.character.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Boss run does not belong to you",
        )

    await db.delete(run)
    await db.commit()


@router.post("/runs/{run_id}/drops", response_model=BossRunDropResponse, status_code=status.HTTP_201_CREATED)
async def add_drop_to_run(
    run_id: UUID,
    drop_data: BossRunDropCreate,
    db: DBSession,
    current_user: CurrentUser,
) -> BossRunDropResponse:
    """Add a drop to an existing boss run."""
    result = await db.execute(
        select(BossRun)
        .where(BossRun.id == run_id)
        .options(selectinload(BossRun.character))
    )
    run = result.scalar_one_or_none()

    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Boss run not found",
        )

    if run.character.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Boss run does not belong to you",
        )

    # Verify item exists
    item_result = await db.execute(select(Item).where(Item.id == drop_data.item_id))
    item = item_result.scalar_one_or_none()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )

    drop = BossRunDrop(
        boss_run_id=run_id,
        item_id=drop_data.item_id,
        quantity=drop_data.quantity,
    )
    db.add(drop)
    await db.commit()
    await db.refresh(drop)

    return BossRunDropResponse(
        id=drop.id,
        item_id=drop.item_id,
        item_name=item.name,
        quantity=drop.quantity,
    )


@router.get("/weekly", response_model=WeeklySummaryResponse)
async def get_weekly_progress(
    db: DBSession,
    current_user: CurrentUser,
    character_id: UUID | None = Query(None, description="Filter by character"),
) -> WeeklySummaryResponse:
    """
    Get weekly boss progress for the current user.
    Shows which bosses have been cleared and total meso earned.
    """
    week_start = get_current_week_start()
    week_end = week_start + timedelta(days=6)

    # Get user's characters
    char_query = select(Character).where(Character.user_id == current_user.id)
    if character_id:
        char_query = char_query.where(Character.id == character_id)

    char_result = await db.execute(char_query)
    characters = {c.id: c for c in char_result.scalars().all()}

    if not characters:
        return WeeklySummaryResponse(
            week_start=week_start,
            week_end=week_end,
            total_bosses=0,
            cleared_count=0,
            total_meso=0,
            progress=[],
        )

    # Get all weekly bosses
    boss_result = await db.execute(
        select(Boss)
        .where(Boss.reset_type == "weekly", Boss.is_active == True)
        .order_by(Boss.sort_order, Boss.name)
    )
    bosses = boss_result.scalars().all()

    # Get clears for this week
    clears_result = await db.execute(
        select(BossRun)
        .where(
            BossRun.character_id.in_(characters.keys()),
            BossRun.week_start == week_start,
            BossRun.is_clear == True,
        )
        .options(selectinload(BossRun.character))
    )
    clears = {(c.boss_id, c.character_id): c for c in clears_result.scalars().all()}

    # Build progress list
    progress = []
    total_meso = 0
    cleared_count = 0

    for boss in bosses:
        # Check if cleared by any character
        cleared = False
        cleared_at = None
        cleared_char_id = None
        cleared_char_name = None

        for char_id in characters.keys():
            key = (boss.id, char_id)
            if key in clears:
                cleared = True
                cleared_at = clears[key].cleared_at
                cleared_char_id = char_id
                cleared_char_name = characters[char_id].character_name
                if boss.crystal_meso:
                    total_meso += boss.crystal_meso // clears[key].party_size
                break

        if cleared:
            cleared_count += 1

        progress.append(
            WeeklyBossProgressResponse(
                boss_id=boss.id,
                boss_name=boss.name,
                boss_difficulty=boss.difficulty,
                reset_type=boss.reset_type,
                crystal_meso=boss.crystal_meso,
                cleared=cleared,
                cleared_at=cleared_at,
                character_id=cleared_char_id,
                character_name=cleared_char_name,
            )
        )

    return WeeklySummaryResponse(
        week_start=week_start,
        week_end=week_end,
        total_bosses=len(bosses),
        cleared_count=cleared_count,
        total_meso=total_meso,
        progress=progress,
    )
