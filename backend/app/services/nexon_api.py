"""
Nexon GMS Open API client for fetching character data.
Handles OCID lookup, character basic info, and character image retrieval.
"""

import httpx
from typing import Optional

from app.config import settings


NEXON_API_BASE = "https://open.api.nexon.com"


class NexonAPIError(Exception):
    """Error when calling Nexon API."""
    pass


class NexonAPIClient:
    """
    Client for Nexon GMS Open API.
    Used to fetch character data (OCID, level, job, icon) from character name and world.
    """

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or settings.nexon_api_key
        if not self.api_key:
            raise NexonAPIError("Nexon API key not configured. Set NEXON_API_KEY in environment.")

    def _get_headers(self) -> dict:
        """Get headers for API requests."""
        return {
            "x-nxopen-api-key": self.api_key,
        }

    async def get_character_ocid(self, character_name: str, world: str) -> str:
        """
        Get character OCID from character name and world.
        
        Args:
            character_name: Character name
            world: World/server name (e.g., "Scania", "Bera")
        
        Returns:
            Character OCID (unique identifier)
        
        Raises:
            NexonAPIError: If API call fails or character not found
        """
        if not self.api_key:
            raise NexonAPIError("Nexon API key not configured")

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                # Map world names to Nexon world codes if needed
                # Common GMS worlds: Scania, Bera, Windia, Khaini, Bellocan, Mardia, Kradia, Yellonde, Demethos, Galicia, Reboot, Reboot2
                world_code = self._normalize_world(world)
                
                response = await client.get(
                    f"{NEXON_API_BASE}/maplestory/v1/id",
                    params={
                        "character_name": character_name,
                    },
                    headers=self._get_headers(),
                )
                response.raise_for_status()
                data = response.json()
                
                if "ocid" not in data:
                    raise NexonAPIError(f"Character '{character_name}' not found")
                
                return data["ocid"]
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 400:
                    raise NexonAPIError(f"Character '{character_name}' not found or invalid")
                elif e.response.status_code == 401:
                    raise NexonAPIError("Invalid Nexon API key")
                elif e.response.status_code == 429:
                    raise NexonAPIError("Nexon API rate limit exceeded")
                else:
                    raise NexonAPIError(f"Nexon API error: {e.response.status_code}")
            except httpx.RequestError as e:
                raise NexonAPIError(f"Failed to connect to Nexon API: {e}")

    async def get_character_basic(self, ocid: str) -> dict:
        """
        Get basic character information from OCID.
        
        Args:
            ocid: Character OCID
        
        Returns:
            Dictionary with character data:
            - character_name: str
            - world_name: str
            - character_class: str (job)
            - character_level: int
            - character_image: str (URL)
            - etc.
        
        Raises:
            NexonAPIError: If API call fails
        """
        if not self.api_key:
            raise NexonAPIError("Nexon API key not configured")

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(
                    f"{NEXON_API_BASE}/maplestory/v1/character/basic",
                    params={"ocid": ocid},
                    headers=self._get_headers(),
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 400:
                    raise NexonAPIError(f"Invalid OCID: {ocid}")
                elif e.response.status_code == 401:
                    raise NexonAPIError("Invalid Nexon API key")
                elif e.response.status_code == 429:
                    raise NexonAPIError("Nexon API rate limit exceeded")
                else:
                    raise NexonAPIError(f"Nexon API error: {e.response.status_code}")
            except httpx.RequestError as e:
                raise NexonAPIError(f"Failed to connect to Nexon API: {e}")

    async def get_character_image(self, ocid: str) -> str:
        """
        Get character image URL from OCID.
        
        Args:
            ocid: Character OCID
        
        Returns:
            Character image URL
        
        Raises:
            NexonAPIError: If API call fails
        """
        if not self.api_key:
            raise NexonAPIError("Nexon API key not configured")

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(
                    f"{NEXON_API_BASE}/maplestory/v1/character/character-image",
                    params={"ocid": ocid},
                    headers=self._get_headers(),
                )
                response.raise_for_status()
                data = response.json()
                return data.get("character_image", "")
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 400:
                    raise NexonAPIError(f"Invalid OCID: {ocid}")
                elif e.response.status_code == 401:
                    raise NexonAPIError("Invalid Nexon API key")
                elif e.response.status_code == 429:
                    raise NexonAPIError("Nexon API rate limit exceeded")
                else:
                    raise NexonAPIError(f"Nexon API error: {e.response.status_code}")
            except httpx.RequestError as e:
                raise NexonAPIError(f"Failed to connect to Nexon API: {e}")

    async def lookup_character(self, character_name: str, world: str) -> dict:
        """
        Complete character lookup: get OCID, basic info, and image.
        
        Args:
            character_name: Character name
            world: World/server name
        
        Returns:
            Dictionary with:
            - ocid: str
            - character_name: str
            - world_name: str
            - character_class: str (job)
            - character_level: int
            - character_image: str (URL)
        """
        # Get OCID
        ocid = await self.get_character_ocid(character_name, world)
        
        # Get basic info (includes image URL)
        basic_info = await self.get_character_basic(ocid)
        
        # Get image URL separately (more reliable)
        try:
            image_url = await self.get_character_image(ocid)
            basic_info["character_image"] = image_url
        except NexonAPIError:
            # If image fetch fails, use the one from basic info if available
            pass
        
        basic_info["ocid"] = ocid
        return basic_info

    def _normalize_world(self, world: str) -> str:
        """
        Normalize world name to match Nexon API format.
        The API might expect specific world codes or names.
        """
        # Common world name mappings
        world_mapping = {
            "scania": "scania",
            "bera": "bera",
            "windia": "windia",
            "khaini": "khaini",
            "bellocan": "bellocan",
            "mardia": "mardia",
            "kradia": "kradia",
            "yellonde": "yellonde",
            "demethos": "demethos",
            "galicia": "galicia",
            "reboot": "reboot",
            "reboot2": "reboot2",
        }
        return world_mapping.get(world.lower(), world.lower())


def get_nexon_client() -> Optional[NexonAPIClient]:
    """Get Nexon API client if API key is configured."""
    try:
        return NexonAPIClient()
    except NexonAPIError:
        return None

