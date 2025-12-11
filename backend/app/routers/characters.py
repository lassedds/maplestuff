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
)

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
        .order_by(Character.is_main.desc(), Character.character_name)
    )
    characters = result.scalars().all()

    return CharacterListResponse(
        characters=[CharacterResponse.model_validate(c) for c in characters],
        total=len(characters),
    )


@router.post("", response_model=CharacterResponse, status_code=status.HTTP_201_CREATED)
async def create_character(
    character_in: CharacterCreate,
    db: DBSession,
    current_user: CurrentUser,
) -> CharacterResponse:
    """Create a new character for the current user."""
    character = Character(
        user_id=current_user.id,
        character_name=character_in.character_name,
        world=character_in.world,
        job=character_in.job,
        level=character_in.level,
        is_main=character_in.is_main,
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
