"""
Character XP tracking router - uses Nexon rankings API to track daily XP.
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
from app.models.character import Character
from app.models.character_xp_snapshot import CharacterXPSnapshot
from app.schemas.character_xp import (
    CharacterXPSnapshotCreate,
    CharacterXPSnapshot as CharacterXPSnapshotSchema,
    CharacterXPSnapshotListResponse,
    CharacterXPDailyGain,
    CharacterXPHistoryResponse,
    CharacterXPOverview,
    CharacterXPOverviewListResponse,
)
from app.services.nexon_rankings_scraper import NexonRankingsScraper, NexonRankingsScraperError
from app.services.xp_table import load_xp_table

router = APIRouter(prefix="/api/character-xp", tags=["character-xp"])


@router.post("/snapshot", response_model=CharacterXPSnapshotSchema, status_code=201)
async def create_xp_snapshot(
    data: CharacterXPSnapshotCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new XP snapshot for a character."""
    
    # Verify character belongs to user
    result = await db.execute(
        select(Character).where(
            Character.id == data.character_id,
            Character.user_id == current_user.id,
        )
    )
    character = result.scalar_one_or_none()
    if not character:
        raise HTTPException(
            status_code=404,
            detail="Character not found or does not belong to you",
        )
    
    # Check if snapshot already exists for this date
    existing = await db.scalar(
        select(CharacterXPSnapshot).where(
            CharacterXPSnapshot.character_id == data.character_id,
            CharacterXPSnapshot.snapshot_date == data.snapshot_date,
        )
    )
    
    if existing:
        # Update existing snapshot
        existing.total_xp = data.total_xp
        if data.level is not None:
            existing.level = data.level
        await db.commit()
        await db.refresh(existing)
        return existing
    
    # Create new snapshot
    snapshot = CharacterXPSnapshot(
        character_id=data.character_id,
        snapshot_date=data.snapshot_date,
        total_xp=data.total_xp,
        level=data.level,
    )
    
    db.add(snapshot)
    await db.commit()
    await db.refresh(snapshot)
    
    return snapshot


@router.post("/fetch/{character_id}", response_model=CharacterXPSnapshotSchema, status_code=201)
async def fetch_character_xp(
    character_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Fetch current XP from Nexon rankings API and create a snapshot."""
    
    # Verify character belongs to user
    result = await db.execute(
        select(Character).where(
            Character.id == character_id,
            Character.user_id == current_user.id,
        )
    )
    character = result.scalar_one_or_none()
    if not character:
        raise HTTPException(
            status_code=404,
            detail="Character not found or does not belong to you",
        )
    
    # Fetch XP from Nexon rankings API
    scraper = NexonRankingsScraper()
    try:
        character_data = await scraper.lookup_character(character.character_name, character.world)
        await scraper.close()
    except NexonRankingsScraperError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to fetch character data from Nexon: {str(e)}",
        )
    
    # Extract XP from response (the rankings API exposes "exp")
    exp = (
        character_data.get("exp")
        or character_data.get("experience")
        or character_data.get("totalExp")
    )
    if exp is None:
        # Gracefully report what we received to aid debugging
        raise HTTPException(
            status_code=400,
            detail="XP data not found in Nexon API response (expected 'exp'/'experience'/'totalExp')",
        )
    
    # Create snapshot for today
    snapshot_date = date.today()
    total_xp = Decimal(str(exp))
    level = character_data.get("level") or character.level
    
    # Check if snapshot already exists for today
    existing = await db.scalar(
        select(CharacterXPSnapshot).where(
            CharacterXPSnapshot.character_id == character_id,
            CharacterXPSnapshot.snapshot_date == snapshot_date,
        )
    )
    
    if existing:
        # Update existing snapshot
        existing.total_xp = total_xp
        if level is not None:
            existing.level = level
        await db.commit()
        await db.refresh(existing)
        return existing
    
    # Create new snapshot
    snapshot = CharacterXPSnapshot(
        character_id=character_id,
        snapshot_date=snapshot_date,
        total_xp=total_xp,
        level=level,
    )
    
    db.add(snapshot)
    await db.commit()
    await db.refresh(snapshot)
    
    return snapshot


@router.get("/history/{character_id}", response_model=CharacterXPHistoryResponse)
async def get_character_xp_history(
    character_id: UUID,
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get XP history for a character with daily gains."""
    
    # Verify character belongs to user
    result = await db.execute(
        select(Character).where(
            Character.id == character_id,
            Character.user_id == current_user.id,
        )
    )
    character = result.scalar_one_or_none()
    if not character:
        raise HTTPException(
            status_code=404,
            detail="Character not found or does not belong to you",
        )
    
    # Get snapshots ordered by date
    cutoff_date = date.today() - timedelta(days=days)
    result = await db.execute(
        select(CharacterXPSnapshot)
        .where(
            CharacterXPSnapshot.character_id == character_id,
            CharacterXPSnapshot.snapshot_date >= cutoff_date,
        )
        .order_by(CharacterXPSnapshot.snapshot_date)
    )
    snapshots = result.scalars().all()
    
    if not snapshots:
        return CharacterXPHistoryResponse(
            character_id=character_id,
            character_name=character.character_name,
            daily_gains=[],
            total_days=0,
            average_daily_xp=Decimal('0'),
            total_xp_gained=Decimal('0'),
        )
    
    # Calculate daily gains
    daily_gains = []
    total_xp_gained = Decimal('0')
    
    for i in range(1, len(snapshots)):
        prev_snapshot = snapshots[i - 1]
        curr_snapshot = snapshots[i]
        
        xp_gained = curr_snapshot.total_xp - prev_snapshot.total_xp
        
        # Only count positive gains (ignore level resets or data errors)
        if xp_gained > 0:
            daily_gains.append(CharacterXPDailyGain(
                date=curr_snapshot.snapshot_date,
                xp_gained=xp_gained,
                level=curr_snapshot.level,
            ))
            total_xp_gained += xp_gained
    
    # Calculate average
    average_daily_xp = total_xp_gained / len(daily_gains) if daily_gains else Decimal('0')
    
    return CharacterXPHistoryResponse(
        character_id=character_id,
        character_name=character.character_name,
        daily_gains=daily_gains,
        total_days=len(daily_gains),
        average_daily_xp=average_daily_xp,
        total_xp_gained=total_xp_gained,
    )


@router.get("/overview", response_model=CharacterXPOverviewListResponse)
async def get_characters_xp_overview(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get XP overview for all user's characters."""
    # Try to load XP table; if missing, we still return overviews without progress %
    xp_table = None
    cumulative_xp = None
    try:
        xp_table = load_xp_table()
        # Precompute cumulative XP start per level
        cumulative_xp = {}
        running = Decimal('0')
        for lvl in sorted(xp_table.keys()):
            cumulative_xp[lvl] = running
            running += xp_table[lvl]['actual']
    except FileNotFoundError:
        xp_table = None
        cumulative_xp = None
    
    # Get all characters
    result = await db.execute(
        select(Character)
        .where(Character.user_id == current_user.id)
        .order_by(Character.is_main.desc(), Character.character_name)
    )
    characters = result.scalars().all()
    
    overviews = []
    
    for character in characters:
        # Get latest snapshot
        latest_result = await db.execute(
            select(CharacterXPSnapshot)
            .where(CharacterXPSnapshot.character_id == character.id)
            .order_by(desc(CharacterXPSnapshot.snapshot_date))
            .limit(1)
        )
        latest_snapshot = latest_result.scalar_one_or_none()
        
        # Get today's snapshot
        today_result = await db.execute(
            select(CharacterXPSnapshot)
            .where(
                CharacterXPSnapshot.character_id == character.id,
                CharacterXPSnapshot.snapshot_date == date.today(),
            )
        )
        today_snapshot = today_result.scalar_one_or_none()
        
        # Get yesterday's snapshot
        yesterday_result = await db.execute(
            select(CharacterXPSnapshot)
            .where(
                CharacterXPSnapshot.character_id == character.id,
                CharacterXPSnapshot.snapshot_date == date.today() - timedelta(days=1),
            )
        )
        yesterday_snapshot = yesterday_result.scalar_one_or_none()
        
        # Calculate XP gains
        xp_today = None
        xp_yesterday = None
        
        if today_snapshot and yesterday_snapshot:
            xp_today = today_snapshot.total_xp - yesterday_snapshot.total_xp
        elif today_snapshot and latest_snapshot and latest_snapshot.snapshot_date < date.today():
            xp_today = today_snapshot.total_xp - latest_snapshot.total_xp
        
        if yesterday_snapshot:
            day_before_yesterday_result = await db.execute(
                select(CharacterXPSnapshot)
                .where(
                    CharacterXPSnapshot.character_id == character.id,
                    CharacterXPSnapshot.snapshot_date == date.today() - timedelta(days=2),
                )
            )
            day_before_yesterday_snapshot = day_before_yesterday_result.scalar_one_or_none()
            
            if day_before_yesterday_snapshot:
                xp_yesterday = yesterday_snapshot.total_xp - day_before_yesterday_snapshot.total_xp
        
        # Calculate average XP (last 7 days)
        seven_days_ago = date.today() - timedelta(days=7)
        recent_snapshots_result = await db.execute(
            select(CharacterXPSnapshot)
            .where(
                CharacterXPSnapshot.character_id == character.id,
                CharacterXPSnapshot.snapshot_date >= seven_days_ago,
            )
            .order_by(CharacterXPSnapshot.snapshot_date)
        )
        recent_snapshots = recent_snapshots_result.scalars().all()
        
        average_xp = None
        total_xp_gained = None
        days_tracked = len(recent_snapshots)
        progress_percent = None
        
        if len(recent_snapshots) >= 2:
            total_gain = recent_snapshots[-1].total_xp - recent_snapshots[0].total_xp
            total_xp_gained = total_gain
            average_xp = total_gain / (len(recent_snapshots) - 1) if len(recent_snapshots) > 1 else Decimal('0')
        
        # Compute % into current level if we have XP table, current XP, and level
        if xp_table and cumulative_xp and latest_snapshot and latest_snapshot.total_xp is not None and latest_snapshot.level:
            lvl = latest_snapshot.level
            if lvl in xp_table and lvl in cumulative_xp:
                xp_required = xp_table[lvl]['actual']
                start_xp = cumulative_xp[lvl]
                within_level = latest_snapshot.total_xp - start_xp
                if xp_required > 0:
                    pct = (within_level / xp_required) * Decimal('100')
                    if pct < 0:
                        pct = Decimal('0')
                    if pct > 100:
                        pct = Decimal('100')
                    progress_percent = pct
        # Fallback: if no XP table, just default to 100% so UI shows something
        elif latest_snapshot:
            progress_percent = Decimal('100')
        
        overviews.append(CharacterXPOverview(
            character_id=character.id,
            character_name=character.character_name,
            world=character.world,
            job=character.job,
            level=latest_snapshot.level if latest_snapshot else character.level,
            character_icon_url=character.character_icon_url,
            current_xp=latest_snapshot.total_xp if latest_snapshot else None,
            xp_today=xp_today if xp_today and xp_today > 0 else None,
            xp_yesterday=xp_yesterday if xp_yesterday and xp_yesterday > 0 else None,
            average_xp=average_xp if average_xp and average_xp > 0 else None,
            total_xp_gained=total_xp_gained if total_xp_gained and total_xp_gained > 0 else None,
            progress_percent=progress_percent,
            days_tracked=days_tracked,
        ))
    
    return CharacterXPOverviewListResponse(characters=overviews)
