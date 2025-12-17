"""
MapleStory.io API proxy endpoints.
Provides access to item sprites, character renders, etc.
"""

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from typing import Optional

from app.services.maplestory_api import get_maplestory_client, MapleStoryAPIError

router = APIRouter(prefix="/maplestory", tags=["maplestory"])


@router.get("/item/{item_id}/sprite")
async def get_item_sprite(
    item_id: int,
    region: str = Query("GMS", description="Server region (GMS, KMS, etc.)"),
    version: str = Query("latest", description="Game version"),
    resize: Optional[int] = Query(None, description="Resize dimension (e.g., 64 for 64x64)"),
):
    """
    Get item sprite URL and redirect to it.
    """
    client = get_maplestory_client()
    try:
        url = client.get_item_sprite_url(item_id, region, version, resize)
        return RedirectResponse(url=url, status_code=status.HTTP_302_FOUND)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get item sprite: {e}",
        )


@router.get("/item/{item_id}/info")
async def get_item_info(
    item_id: int,
    region: str = Query("GMS", description="Server region"),
    version: str = Query("latest", description="Game version"),
):
    """
    Get detailed item information from MapleStory.io API.
    """
    client = get_maplestory_client()
    try:
        info = await client.get_item_info(item_id, region, version)
        if info is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item {item_id} not found",
            )
        return info
    except MapleStoryAPIError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/item/{item_id}/sprite-url")
async def get_item_sprite_url(
    item_id: int,
    region: str = Query("GMS", description="Server region"),
    version: str = Query("latest", description="Game version"),
    resize: Optional[int] = Query(None, description="Resize dimension"),
):
    """
    Get item sprite URL (returns JSON with URL instead of redirecting).
    """
    client = get_maplestory_client()
    try:
        url = client.get_item_sprite_url(item_id, region, version, resize)
        return {"item_id": item_id, "sprite_url": url}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get item sprite URL: {e}",
        )


