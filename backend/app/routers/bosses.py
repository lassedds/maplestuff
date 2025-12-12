"""
Boss API endpoints for GMSTracker.
Public read-only endpoints for boss data.
"""

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.dependencies import DBSession
from app.models import Boss, BossDropTable, Item
from app.schemas import (
    BossResponse,
    BossWithDropsResponse,
    BossListResponse,
    ItemDropResponse,
)

router = APIRouter(prefix="/bosses", tags=["bosses"])


@router.get("", response_model=BossListResponse)
async def list_bosses(
    db: DBSession,
    reset_type: str | None = Query(None, description="Filter by reset type (daily, weekly, monthly)"),
    active_only: bool = Query(True, description="Only return active bosses"),
) -> BossListResponse:
    """
    List all bosses.
    Optionally filter by reset type (daily, weekly, monthly).
    """
    query = select(Boss).order_by(Boss.sort_order, Boss.name)

    if reset_type:
        query = query.where(Boss.reset_type == reset_type)

    if active_only:
        query = query.where(Boss.is_active == True)

    result = await db.execute(query)
    bosses = result.scalars().all()

    return BossListResponse(
        bosses=[BossResponse.model_validate(b) for b in bosses],
        total=len(bosses),
    )


@router.get("/{boss_id}", response_model=BossWithDropsResponse)
async def get_boss(
    boss_id: int,
    db: DBSession,
) -> BossWithDropsResponse:
    """
    Get a specific boss by ID with its drop table.
    """
    result = await db.execute(
        select(Boss)
        .where(Boss.id == boss_id)
        .options(selectinload(Boss.drop_table).selectinload(BossDropTable.item))
    )
    boss = result.scalar_one_or_none()

    if boss is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Boss not found",
        )

    # Build drop list
    drops = [
        ItemDropResponse(
            item_id=drop.item_id,
            item_name=drop.item.name,
            is_guaranteed=drop.is_guaranteed,
        )
        for drop in boss.drop_table
    ]

    return BossWithDropsResponse(
        id=boss.id,
        name=boss.name,
        difficulty=boss.difficulty,
        reset_type=boss.reset_type,
        party_size=boss.party_size,
        crystal_meso=boss.crystal_meso,
        image_url=boss.image_url,
        sort_order=boss.sort_order,
        is_active=boss.is_active,
        drops=drops,
    )


@router.get("/by-name/{name}", response_model=list[BossResponse])
async def get_bosses_by_name(
    name: str,
    db: DBSession,
) -> list[BossResponse]:
    """
    Get all difficulty variants of a boss by name.
    Example: /bosses/by-name/Lucid returns Easy, Normal, Hard Lucid.
    """
    result = await db.execute(
        select(Boss)
        .where(Boss.name.ilike(f"%{name}%"))
        .order_by(Boss.sort_order)
    )
    bosses = result.scalars().all()

    if not bosses:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No bosses found matching '{name}'",
        )

    return [BossResponse.model_validate(b) for b in bosses]
