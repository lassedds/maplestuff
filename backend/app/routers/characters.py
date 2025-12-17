"""
Character management API endpoints for GMSTracker.
"""

from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError

from app.dependencies import DBSession, CurrentUser
from app.models import Character
from app.schemas import (
    CharacterCreate,
    CharacterUpdate,
    CharacterResponse,
    CharacterListResponse,
    CharacterLookupRequest,
    CharacterLookupResponse,
    CharacterReorderRequest,
)
# Temporarily disabled: from app.services.nexon_api import get_nexon_client, NexonAPIError
import os

router = APIRouter(prefix="/characters", tags=["characters"])


@router.get("", response_model=CharacterListResponse)
async def list_characters(
    db: DBSession,
    current_user: CurrentUser,
) -> CharacterListResponse:
    """List all characters for the current user."""
    result = await db.execute(
        select(Character)
        .where(Character.user_id == current_user.id)
        .order_by(
            Character.is_main.desc(),  # Keep mains at the top
            Character.sort_order,
            Character.character_name,
        )
    )
    characters = result.scalars().all()

    return CharacterListResponse(
        characters=[CharacterResponse.model_validate(c) for c in characters],
        total=len(characters),
    )


@router.post("/lookup", response_model=CharacterLookupResponse)
async def lookup_character(
    lookup_request: CharacterLookupRequest,
) -> CharacterLookupResponse:
    """
    Look up character data from Nexon Rankings API.
    
    Returns character info (level, job, icon) for preview.
    """
    from app.services.nexon_rankings_scraper import (
        get_nexon_rankings_scraper,
        NexonRankingsScraperError,
    )
    import json
    import os
    from datetime import datetime
    
    # #region agent log
    log_path = "/app/.cursor/debug.log"
    try:
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"characters.py:lookup_character:scraper_start","message":"Starting Nexon scraper lookup","data":{"character_name":lookup_request.character_name,"world":lookup_request.world},"timestamp":int(datetime.now().timestamp()*1000)})+"\n")
    except: pass
    # #endregion
    
    scraper = get_nexon_rankings_scraper()
    
    # #region agent log
    try:
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"characters.py:lookup_character:scraper_check","message":"Scraper instance check","data":{"has_scraper":scraper is not None},"timestamp":int(datetime.now().timestamp()*1000)})+"\n")
    except: pass
    # #endregion
    
    if not scraper:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Nexon rankings scraper is not available.",
        )
    
    try:
        data = await scraper.lookup_character(
            lookup_request.character_name,
            lookup_request.world,
        )
        
        # #region agent log
        try:
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"characters.py:lookup_character:scraper_success","message":"Scraper returned data","data":{"data_keys":list(data.keys()) if data else [],"world":data.get("world") if data else None,"level":data.get("level") if data else None},"timestamp":int(datetime.now().timestamp()*1000)})+"\n")
        except: pass
        # #endregion
        
        return CharacterLookupResponse(
            character_name=data.get("character_name", lookup_request.character_name),
            world=data.get("world") or lookup_request.world,
            level=data.get("level"),
            job=data.get("job"),
            character_image=data.get("character_image"),
            character_icon_url=data.get("character_icon_url") or data.get("character_image"),
            nexon_ocid=data.get("nexon_ocid"),
        )
    except NexonRankingsScraperError as e:
        # #region agent log
        try:
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"characters.py:lookup_character:scraper_error","message":"Scraper error caught","data":{"error":str(e),"error_type":type(e).__name__},"timestamp":int(datetime.now().timestamp()*1000)})+"\n")
        except: pass
        # #endregion
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character not found: {str(e)}",
        )
    finally:
        await scraper.close()


@router.post("", response_model=CharacterResponse, status_code=status.HTTP_201_CREATED)
async def create_character(
    character_in: CharacterCreate,
    db: DBSession,
    current_user: CurrentUser,
    use_nexon_api: bool = True,
) -> CharacterResponse:
    """
    Create a new character for the current user.
    If use_nexon_api is True and only name/world provided, fetches data from Nexon Rankings API.
    """
    nexon_ocid = None
    character_icon_url = None
    job = character_in.job
    level = character_in.level

    # Always try to fetch icon URL and other data from Nexon Rankings API if enabled
    if use_nexon_api:
        from app.services.nexon_rankings_scraper import (
            get_nexon_rankings_scraper,
            NexonRankingsScraperError,
        )
        
        scraper = get_nexon_rankings_scraper()
        if scraper:
            try:
                data = await scraper.lookup_character(
                    character_in.character_name,
                    character_in.world,
                )
                # Always fetch icon URL if available
                fetched_icon_url = data.get("character_icon_url") or data.get("character_image")
                if fetched_icon_url:
                    character_icon_url = fetched_icon_url
                # Only update job/level if not already provided
                if not job:
                    job = data.get("job")
                if not level:
                    level = data.get("level")
                nexon_ocid = data.get("nexon_ocid")
            except NexonRankingsScraperError:
                # If API fails, continue with manual entry
                pass
            finally:
                await scraper.close()

    # Place new characters at the end of the user's list by default
    max_order_result = await db.execute(
        select(func.coalesce(func.max(Character.sort_order), -1)).where(Character.user_id == current_user.id)
    )
    next_sort_order = (max_order_result.scalar() or -1) + 1

    character = Character(
        user_id=current_user.id,
        character_name=character_in.character_name,
        world=character_in.world,
        job=job,
        level=level,
        is_main=character_in.is_main,
        nexon_ocid=nexon_ocid,
        character_icon_url=character_icon_url,
        sort_order=next_sort_order,
    )

    # If this is set as main, unset other mains
    if character_in.is_main:
        await _unset_other_mains(db, current_user.id)

    try:
        db.add(character)
        await db.commit()
        await db.refresh(character)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Character '{character_in.character_name}' on {character_in.world} already exists",
        )

    return CharacterResponse.model_validate(character)


@router.get("/{character_id}", response_model=CharacterResponse)
async def get_character(
    character_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
) -> CharacterResponse:
    """Get a specific character by ID."""
    character = await _get_user_character(db, current_user.id, character_id)
    return CharacterResponse.model_validate(character)


@router.put("/{character_id}", response_model=CharacterResponse)
async def update_character(
    character_id: UUID,
    character_in: CharacterUpdate,
    db: DBSession,
    current_user: CurrentUser,
) -> CharacterResponse:
    """Update a character."""
    character = await _get_user_character(db, current_user.id, character_id)

    # Update fields if provided
    if character_in.job is not None:
        character.job = character_in.job
    if character_in.level is not None:
        character.level = character_in.level
    if character_in.is_main is not None:
        if character_in.is_main:
            await _unset_other_mains(db, current_user.id, exclude_id=character_id)
        character.is_main = character_in.is_main

    await db.commit()
    await db.refresh(character)

    return CharacterResponse.model_validate(character)


@router.post("/{character_id}/refresh", response_model=CharacterResponse)
async def refresh_character(
    character_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
) -> CharacterResponse:
    """
    Refresh character data from Nexon Rankings API.
    Updates level, job, and icon.
    """
    character = await _get_user_character(db, current_user.id, character_id)

    from app.services.nexon_rankings_scraper import (
        get_nexon_rankings_scraper,
        NexonRankingsScraperError,
    )
    
    scraper = get_nexon_rankings_scraper()
    if not scraper:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Nexon rankings scraper is not available.",
        )

    try:
        # Get updated character data
        data = await scraper.lookup_character(
            character.character_name,
            character.world,
        )

        # Update character fields
        character.job = data.get("job") or character.job
        character.level = data.get("level") or character.level
        character.character_icon_url = data.get("character_icon_url") or data.get("character_image") or character.character_icon_url
        character.nexon_ocid = data.get("nexon_ocid") or character.nexon_ocid

        await db.commit()
        await db.refresh(character)

        return CharacterResponse.model_validate(character)
    except NexonRankingsScraperError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to refresh character: {e}",
        )
    finally:
        await scraper.close()


@router.post("/reorder", status_code=status.HTTP_204_NO_CONTENT)
async def reorder_characters(
    reorder_request: CharacterReorderRequest,
    db: DBSession,
    current_user: CurrentUser,
) -> None:
    """
    Update the display order for the current user's characters.
    Accepts an ordered list of character IDs. Missing IDs are appended in their current order.
    """
    requested_ids = reorder_request.character_ids

    # Fetch all character IDs for the current user
    result = await db.execute(
        select(Character.id, Character.sort_order)
        .where(Character.user_id == current_user.id)
        .order_by(Character.sort_order, Character.created_at)
    )
    user_characters = result.all()
    user_ids = [row[0] for row in user_characters]

    # Ensure the user is not trying to reorder characters they don't own
    unknown_ids = set(requested_ids) - set(user_ids)
    if unknown_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid character IDs in reorder request",
        )

    # Build the final order: requested IDs first, then any missing in their prior order
    remaining_ids = [cid for cid in user_ids if cid not in requested_ids]
    final_ids = [*requested_ids, *remaining_ids]

    # Load characters into a map for quick updates
    result = await db.execute(
        select(Character).where(
            Character.user_id == current_user.id,
            Character.id.in_(final_ids),
        )
    )
    char_map = {c.id: c for c in result.scalars()}

    for idx, cid in enumerate(final_ids):
        character = char_map.get(cid)
        if character:
            character.sort_order = idx

    await db.commit()


@router.delete("/{character_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_character(
    character_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
) -> None:
    """Delete a character."""
    character = await _get_user_character(db, current_user.id, character_id)
    await db.delete(character)
    await db.commit()


# Helper functions

async def _get_user_character(
    db: DBSession,
    user_id: UUID,
    character_id: UUID,
) -> Character:
    """Get a character belonging to a user, or raise 404."""
    result = await db.execute(
        select(Character).where(
            Character.id == character_id,
            Character.user_id == user_id,
        )
    )
    character = result.scalar_one_or_none()

    if character is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found",
        )

    return character


async def _unset_other_mains(
    db: DBSession,
    user_id: UUID,
    exclude_id: UUID | None = None,
) -> None:
    """Unset is_main for all other characters of a user."""
    query = select(Character).where(
        Character.user_id == user_id,
        Character.is_main == True,
    )
    if exclude_id:
        query = query.where(Character.id != exclude_id)

    result = await db.execute(query)
    for char in result.scalars():
        char.is_main = False
