"""
XP Tracker router - handles daily XP tracking endpoints.
"""

from datetime import date, timedelta
from decimal import Decimal
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.xp_entry import XPEntry
from app.schemas.xp_entry import (
    XPEntryCreate,
    XPEntryUpdate,
    XPEntry as XPEntrySchema,
    XPEntryListResponse,
    XPStats,
)
from app.services.xp_table import calculate_xp_gained
from app.services.epic_dungeon import get_epic_dungeon_xp

router = APIRouter(prefix="/api/xp", tags=["xp"])


@router.post("", response_model=XPEntrySchema, status_code=201)
async def create_xp_entry(
    data: XPEntryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new XP entry."""
    
    # Validate percentages
    if data.new_percent <= data.old_percent:
        raise HTTPException(
            status_code=400,
            detail="New percent must be greater than old percent"
        )
    
    # Calculate XP gained
    xp_gained = calculate_xp_gained(
        data.level,
        data.old_percent,
        data.new_percent
    )
    
    # Calculate Epic Dungeon XP if applicable
    epic_dungeon_xp_trillions = None
    epic_dungeon_xp_billions = None
    
    if data.epic_dungeon:
        epic_xp = get_epic_dungeon_xp(data.level, data.epic_dungeon_multiplier)
        if epic_xp:
            epic_dungeon_xp_trillions = epic_xp['trillions']
            epic_dungeon_xp_billions = epic_xp['billions']
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Epic Dungeon XP not available for level {data.level}"
            )
    
    # Calculate total daily XP
    total_trillions = xp_gained['trillions'] + (epic_dungeon_xp_trillions or Decimal('0'))
    total_billions = xp_gained['billions'] + (epic_dungeon_xp_billions or Decimal('0'))
    
    # Check if entry already exists for this date
    existing = await db.scalar(
        select(XPEntry).where(
            XPEntry.user_id == current_user.id,
            XPEntry.entry_date == data.entry_date
        )
    )
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"XP entry already exists for date {data.entry_date}"
        )
    
    # Create entry
    entry = XPEntry(
        user_id=str(current_user.id),
        entry_date=data.entry_date,
        level=data.level,
        old_percent=data.old_percent,
        new_percent=data.new_percent,
        xp_gained_trillions=xp_gained['trillions'],
        xp_gained_billions=xp_gained['billions'],
        epic_dungeon=data.epic_dungeon,
        epic_dungeon_xp_trillions=epic_dungeon_xp_trillions,
        epic_dungeon_xp_billions=epic_dungeon_xp_billions,
        epic_dungeon_multiplier=data.epic_dungeon_multiplier,
        total_daily_xp_trillions=total_trillions,
        total_daily_xp_billions=total_billions,
    )
    
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    
    return entry


@router.get("", response_model=XPEntryListResponse)
async def get_xp_entries(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get XP entries for the current user."""
    
    query = select(XPEntry).where(XPEntry.user_id == current_user.id)
    
    if start_date:
        query = query.where(XPEntry.entry_date >= start_date)
    if end_date:
        query = query.where(XPEntry.entry_date <= end_date)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)
    
    # Get entries
    query = query.order_by(desc(XPEntry.entry_date)).limit(limit).offset(offset)
    result = await db.execute(query)
    entries = result.scalars().all()
    
    return XPEntryListResponse(entries=entries, total=total)


@router.get("/stats", response_model=XPStats)
async def get_xp_stats(
    days: int = Query(7, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get XP statistics for the last N days."""
    
    cutoff_date = date.today() - timedelta(days=days)
    
    # Get entries from last N days
    query = select(XPEntry).where(
        XPEntry.user_id == current_user.id,
        XPEntry.entry_date >= cutoff_date
    )
    
    result = await db.execute(query)
    entries = result.scalars().all()
    
    if not entries:
        return XPStats(
            seven_day_average_trillions=Decimal('0'),
            seven_day_average_billions=Decimal('0'),
            total_xp_trillions=Decimal('0'),
            total_xp_billions=Decimal('0'),
            entry_count=0,
        )
    
    # Calculate totals
    total_trillions = sum(e.total_daily_xp_trillions for e in entries)
    total_billions = sum(e.total_daily_xp_billions for e in entries)
    
    # Calculate average
    avg_trillions = total_trillions / len(entries)
    avg_billions = total_billions / len(entries)
    
    return XPStats(
        seven_day_average_trillions=avg_trillions,
        seven_day_average_billions=avg_billions,
        total_xp_trillions=total_trillions,
        total_xp_billions=total_billions,
        entry_count=len(entries),
    )


@router.get("/{entry_id}", response_model=XPEntrySchema)
async def get_xp_entry(
    entry_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific XP entry."""
    
    entry = await db.scalar(
        select(XPEntry).where(
            XPEntry.id == entry_id,
            XPEntry.user_id == current_user.id
        )
    )
    
    if not entry:
        raise HTTPException(status_code=404, detail="XP entry not found")
    
    return entry


@router.put("/{entry_id}", response_model=XPEntrySchema)
async def update_xp_entry(
    entry_id: UUID,
    data: XPEntryUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update an XP entry."""
    
    entry = await db.scalar(
        select(XPEntry).where(
            XPEntry.id == entry_id,
            XPEntry.user_id == current_user.id
        )
    )
    
    if not entry:
        raise HTTPException(status_code=404, detail="XP entry not found")
    
    # Update fields
    if data.level is not None:
        entry.level = data.level
    if data.old_percent is not None:
        entry.old_percent = data.old_percent
    if data.new_percent is not None:
        entry.new_percent = data.new_percent
    if data.epic_dungeon is not None:
        entry.epic_dungeon = data.epic_dungeon
    if data.epic_dungeon_multiplier is not None:
        entry.epic_dungeon_multiplier = data.epic_dungeon_multiplier
    
    # Recalculate XP if percentages or level changed
    if any([data.level, data.old_percent, data.new_percent]):
        xp_gained = calculate_xp_gained(
            entry.level,
            entry.old_percent,
            entry.new_percent
        )
        entry.xp_gained_trillions = xp_gained['trillions']
        entry.xp_gained_billions = xp_gained['billions']
    
    # Recalculate Epic Dungeon XP if applicable
    if entry.epic_dungeon:
        epic_xp = get_epic_dungeon_xp(entry.level, entry.epic_dungeon_multiplier)
        if epic_xp:
            entry.epic_dungeon_xp_trillions = epic_xp['trillions']
            entry.epic_dungeon_xp_billions = epic_xp['billions']
        else:
            entry.epic_dungeon_xp_trillions = None
            entry.epic_dungeon_xp_billions = None
    
    # Recalculate total
    entry.total_daily_xp_trillions = entry.xp_gained_trillions + (entry.epic_dungeon_xp_trillions or Decimal('0'))
    entry.total_daily_xp_billions = entry.xp_gained_billions + (entry.epic_dungeon_xp_billions or Decimal('0'))
    
    await db.commit()
    await db.refresh(entry)
    
    return entry


@router.delete("/{entry_id}", status_code=204)
async def delete_xp_entry(
    entry_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete an XP entry."""
    
    entry = await db.scalar(
        select(XPEntry).where(
            XPEntry.id == entry_id,
            XPEntry.user_id == current_user.id
        )
    )
    
    if not entry:
        raise HTTPException(status_code=404, detail="XP entry not found")
    
    await db.delete(entry)
    await db.commit()
