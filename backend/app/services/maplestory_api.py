"""
MapleStory.io API client for fetching sprites, images, and game data.
Public API - no authentication required.
"""

import httpx
from typing import Optional

MAPLESTORY_IO_BASE = "https://maplestory.io/api"


class MapleStoryAPIError(Exception):
    """Error when calling MapleStory.io API."""
    pass


class MapleStoryAPIClient:
    """
    Client for MapleStory.io API.
    Used to fetch item sprites, boss images, character renders, etc.
    """

    def __init__(self, base_url: str = MAPLESTORY_IO_BASE):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=10.0)

    async def get_item_sprite(
        self,
        item_id: int,
        region: str = "GMS",
        version: str = "latest",
        resize: Optional[int] = None,
    ) -> str:
        """
        Get item sprite URL.
        
        Args:
            item_id: MapleStory item ID
            region: Server region (GMS, KMS, etc.)
            version: Game version (default: "latest")
            resize: Optional resize dimension (e.g., 64 for 64x64)
        
        Returns:
            URL to the item sprite image
        """
        url = f"{self.base_url}/{region}/{version}/item/{item_id}/icon"
        if resize:
            url += f"?resize={resize}"
        return url

    async def get_boss_image(
        self,
        boss_name: str,
        region: str = "GMS",
        version: str = "latest",
    ) -> Optional[str]:
        """
        Get boss image URL.
        Note: This is a placeholder - maplestory.io may not have direct boss images.
        You may need to use item sprites or other endpoints.
        
        Args:
            boss_name: Boss name (e.g., "Lucid")
            region: Server region
            version: Game version
        
        Returns:
            URL to boss image if available, None otherwise
        """
        # maplestory.io doesn't have direct boss images, but we can try to find related items
        # For now, return None - you may need to use item sprites or external sources
        return None

    async def get_character_render(
        self,
        character_data: dict,
        region: str = "GMS",
        version: str = "latest",
    ) -> str:
        """
        Get character render URL.
        
        Args:
            character_data: Character data dict with equipment, etc.
            region: Server region
            version: Game version
        
        Returns:
            URL to character render
        """
        # This would require constructing a render request with character data
        # For now, return a placeholder
        # See maplestory.io docs for render API details
        return f"{self.base_url}/{region}/{version}/character/render"

    async def search_items(
        self,
        query: str,
        region: str = "GMS",
        version: str = "latest",
    ) -> list[dict]:
        """
        Search for items by name.
        
        Args:
            query: Search query
            region: Server region
            version: Game version
        
        Returns:
            List of matching items
        """
        # Note: maplestory.io may not have a search endpoint
        # You might need to use your own database for item search
        # This is a placeholder for future implementation
        return []

    async def get_item_info(
        self,
        item_id: int,
        region: str = "GMS",
        version: str = "latest",
    ) -> Optional[dict]:
        """
        Get detailed item information.
        
        Args:
            item_id: MapleStory item ID
            region: Server region
            version: Game version
        
        Returns:
            Item information dict or None if not found
        """
        try:
            url = f"{self.base_url}/{region}/{version}/item/{item_id}"
            response = await self.client.get(url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError:
            return None
        except httpx.RequestError as e:
            raise MapleStoryAPIError(f"Failed to fetch item info: {e}")

    def get_item_sprite_url(
        self,
        item_id: int,
        region: str = "GMS",
        version: str = "latest",
        resize: Optional[int] = None,
    ) -> str:
        """
        Get item sprite URL (synchronous version for use in templates).
        """
        url = f"{self.base_url}/{region}/{version}/item/{item_id}/icon"
        if resize:
            url += f"?resize={resize}"
        return url

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


# Global client instance
_maplestory_client: Optional[MapleStoryAPIClient] = None


def get_maplestory_client() -> MapleStoryAPIClient:
    """Get or create the global MapleStory API client."""
    global _maplestory_client
    if _maplestory_client is None:
        _maplestory_client = MapleStoryAPIClient()
    return _maplestory_client


