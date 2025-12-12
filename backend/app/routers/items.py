"""
Item API endpoints for GMSTracker.
Public read-only endpoints for item data.
"""

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.dependencies import DBSession
from app.models import Item, BossDropTable, Boss
from app.schemas import (
    ItemResponse,
    ItemWithSourcesResponse,
    ItemListResponse,
    BossSourceResponse,
)

router = APIRouter(prefix="/items", tags=["items"])


@router.get("", response_model=ItemListResponse)
async def list_items(
    db: DBSession,
    category: str | None = Query(None, description="Filter by category"),
    rarity: str | None = Query(None, description="Filter by rarity"),
    search: str | None = Query(None, description="Search by name"),
    active_only: bool = Query(True, description="Only return active items"),
) -> ItemListResponse:
    """
    List all items.
    Optionally filter by category, rarity, or search by name.
    """
    query = select(Item).order_by(Item.name)

    if category:
        query = query.where(Item.category == category)

    if rarity:
        query = query.where(Item.rarity == rarity)

    if search:
        query = query.where(Item.name.ilike(f"%{search}%"))

    if active_only:
        query = query.where(Item.is_active == True)

    result = await db.execute(query)
    items = result.scalars().all()

    return ItemListResponse(
        items=[ItemResponse.model_validate(i) for i in items],
        total=len(items),
    )


@router.get("/{item_id}", response_model=ItemWithSourcesResponse)
async def get_item(
    item_id: int,
    db: DBSession,
) -> ItemWithSourcesResponse:
    """
    Get a specific item by ID with its drop sources.
    """
    result = await db.execute(
        select(Item)
        .where(Item.id == item_id)
        .options(selectinload(Item.drop_sources).selectinload(BossDropTable.boss))
    )
    item = result.scalar_one_or_none()

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )

    # Build drop sources list
    sources = [
        BossSourceResponse(
            boss_id=source.boss_id,
            boss_name=source.boss.name,
            boss_difficulty=source.boss.difficulty,
            is_guaranteed=source.is_guaranteed,
        )
        for source in item.drop_sources
    ]

    return ItemWithSourcesResponse(
        id=item.id,
        name=item.name,
        category=item.category,
        subcategory=item.subcategory,
        rarity=item.rarity,
        image_url=item.image_url,
        is_active=item.is_active,
        drop_sources=sources,
    )


@router.get("/by-name/{name}", response_model=list[ItemResponse])
async def get_items_by_name(
    name: str,
    db: DBSession,
) -> list[ItemResponse]:
    """
    Search items by name.
    """
    result = await db.execute(
        select(Item)
        .where(Item.name.ilike(f"%{name}%"))
        .order_by(Item.name)
    )
    items = result.scalars().all()

    if not items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No items found matching '{name}'",
        )

    return [ItemResponse.model_validate(i) for i in items]


@router.get("/categories", response_model=list[str])
async def list_categories(db: DBSession) -> list[str]:
    """
    List all unique item categories.
    """
    result = await db.execute(
        select(Item.category)
        .where(Item.category.isnot(None))
        .distinct()
        .order_by(Item.category)
    )
    categories = result.scalars().all()
    return categories


@router.get("/rarities", response_model=list[str])
async def list_rarities(db: DBSession) -> list[str]:
    """
    List all unique item rarities.
    """
    result = await db.execute(
        select(Item.rarity)
        .where(Item.rarity.isnot(None))
        .distinct()
        .order_by(Item.rarity)
    )
    rarities = result.scalars().all()
    return rarities
