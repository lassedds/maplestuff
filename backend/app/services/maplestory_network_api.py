"""
MapleStory Network API client for fetching GMS character data.
Uses OAuth JWT token for authentication.
"""

import httpx
import json
from typing import Optional

from app.config import settings


# Try different possible base URLs
# Based on research: maplestory.net has a /develop section and uses OAuth
# The API might be at different locations
MAPLESTORY_NETWORK_API_BASE_OPTIONS = [
    "https://api.maplestory.net",
    "https://maplestory.net/api",
    "https://maplestory.net/api/v1",
    "https://maplestory.net/api/v2",
    "https://maplestory.net/develop/api",
    "https://maplestory.net/develop/api/v1",
    "https://maplestory.net",
]
MAPLESTORY_NETWORK_API_BASE = MAPLESTORY_NETWORK_API_BASE_OPTIONS[0]  # Default to first option


class MapleStoryNetworkAPIError(Exception):
    """Error when calling MapleStory Network API."""
    pass


class MapleStoryNetworkAPIClient:
    """
    Client for MapleStory Network API (GMS).
    Used to fetch character data (level, job, icon) from character name and world.
    """

    def __init__(self, access_token: str | None = None):
        self.access_token = access_token or settings.maplestory_network_token
        if not self.access_token:
            raise MapleStoryNetworkAPIError(
                "MapleStory Network access token not configured. Set MAPLESTORY_NETWORK_TOKEN in environment."
            )

    def _get_headers(self) -> dict:
        """Get headers for API requests."""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    async def lookup_character(self, character_name: str, world: str) -> dict:
        """
        Look up character data from MapleStory Network API.
        
        Args:
            character_name: Character name
            world: World/server name (e.g., "Scania", "Bera")
        
        Returns:
            Dictionary with character data:
            - character_name: str
            - world: str
            - level: int
            - job: str
            - character_image: str (URL)
            - etc.
        
        Raises:
            MapleStoryNetworkAPIError: If API call fails
        """
        # #region agent log
        try:
            with open("/app/debug.log", "a", encoding="utf-8") as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"maplestory_network_api.py:40","message":"lookup_character entry","data":{"character_name":character_name,"world":world,"base_url":MAPLESTORY_NETWORK_API_BASE,"has_token":bool(self.access_token)},"timestamp":int(__import__("time").time()*1000)})+"\n")
        except Exception:
            pass
        # #endregion
        
        if not self.access_token:
            raise MapleStoryNetworkAPIError("MapleStory Network access token not configured")

        async with httpx.AsyncClient(timeout=10.0) as client:
            headers = self._get_headers()
            last_error = None
            
            # First, try to access API documentation or root endpoint to understand structure
            # #region agent log
            try:
                with open("/app/debug.log", "a", encoding="utf-8") as f:
                    f.write(json.dumps({"sessionId":"debug-session","runId":"run3","hypothesisId":"O","location":"maplestory_network_api.py:70","message":"Testing API root/documentation endpoints","data":{},"timestamp":int(__import__("time").time()*1000)})+"\n")
            except Exception:
                pass
            # #endregion
            
            # Try to get API info/documentation and follow redirects
            for base_url in MAPLESTORY_NETWORK_API_BASE_OPTIONS:
                for test_path in ["/", "/api", "/api/v1", "/develop", "/docs", "/documentation"]:
                    try:
                        test_url = f"{base_url}{test_path}"
                        test_response = await client.get(test_url, headers=headers, follow_redirects=True)
                        # #region agent log
                        try:
                            with open("/app/debug.log", "a", encoding="utf-8") as f:
                                redirect_url = str(test_response.url) if hasattr(test_response, 'url') else test_url
                                f.write(json.dumps({"sessionId":"debug-session","runId":"run4","hypothesisId":"P","location":"maplestory_network_api.py:95","message":"Testing API info endpoint","data":{"url":test_url,"status_code":test_response.status_code,"final_url":redirect_url},"timestamp":int(__import__("time").time()*1000)})+"\n")
                        except Exception:
                            pass
                        # #endregion
                        if test_response.status_code == 200:
                            # Found something useful
                            pass
                    except:
                        pass
            
            # First, try to get API version info to understand the structure
            # Based on research: API uses version=220, subversion=0, locale=0 for GMS
            # There's a /version/default endpoint that might help
            for base_url in MAPLESTORY_NETWORK_API_BASE_OPTIONS:
                try:
                    version_url = f"{base_url}/version/default"
                    version_response = await client.get(version_url, headers=headers, follow_redirects=True)
                    if version_response.status_code == 200:
                        version_data = version_response.json()
                        # Log version info for debugging
                        try:
                            with open("/app/debug.log", "a", encoding="utf-8") as f:
                                f.write(json.dumps({"sessionId":"debug-session","runId":"run5","hypothesisId":"V","location":"maplestory_network_api.py:115","message":"Found version endpoint","data":{"base_url":base_url,"version_data":version_data},"timestamp":int(__import__("time").time()*1000)})+"\n")
                        except Exception:
                            pass
                except Exception:
                    pass
            
            # Try GraphQL endpoint first (some modern APIs use GraphQL)
            graphql_endpoints = [
                "/graphql",
                "/api/graphql",
                "/api/v1/graphql",
                "/develop/api/graphql",
            ]
            
            for base_url in MAPLESTORY_NETWORK_API_BASE_OPTIONS:
                for graphql_path in graphql_endpoints:
                    try:
                        graphql_url = f"{base_url}{graphql_path}"
                        # Try a GraphQL query for character lookup
                        graphql_query = {
                            "query": """
                                query GetCharacter($name: String!, $world: String!) {
                                    character(name: $name, world: $world) {
                                        name
                                        world
                                        level
                                        job
                                        characterClass
                                        image
                                        icon
                                    }
                                }
                            """,
                            "variables": {
                                "name": character_name,
                                "world": world
                            }
                        }
                        graphql_response = await client.post(
                            graphql_url,
                            json=graphql_query,
                            headers=headers,
                            follow_redirects=True
                        )
                        if graphql_response.status_code == 200:
                            graphql_data = graphql_response.json()
                            if "data" in graphql_data and graphql_data.get("data", {}).get("character"):
                                char_data = graphql_data["data"]["character"]
                                result = {
                                    "character_name": char_data.get("name") or character_name,
                                    "world": char_data.get("world") or world,
                                    "world_name": char_data.get("world") or world,
                                    "level": char_data.get("level"),
                                    "character_level": char_data.get("level"),
                                    "job": char_data.get("job") or char_data.get("characterClass"),
                                    "character_class": char_data.get("job") or char_data.get("characterClass"),
                                    "character_image": char_data.get("image") or char_data.get("icon"),
                                    "character_icon_url": char_data.get("image") or char_data.get("icon"),
                                    "ocid": None,
                                    "nexon_ocid": None,
                                }
                                return result
                    except Exception:
                        pass
            
            # Try different base URLs and endpoint formats
            # Based on API docs, GMS uses version=220, subversion=0, locale=0
            # Common patterns for character/profile APIs:
            endpoint_formats = [
                # Profile/character endpoints (most common)
                ("/api/profiles/{name}", {"world": world, "version": 220, "subversion": 0, "locale": 0}),
                ("/api/profile/{name}", {"world": world, "version": 220, "subversion": 0, "locale": 0}),
                ("/api/characters/{name}", {"world": world, "version": 220, "subversion": 0, "locale": 0}),
                ("/api/character/{name}", {"world": world, "version": 220, "subversion": 0, "locale": 0}),
                # Query parameter variants
                ("/api/profiles", {"character_name": character_name, "world": world, "version": 220, "subversion": 0, "locale": 0}),
                ("/api/characters", {"name": character_name, "world": world, "version": 220, "subversion": 0, "locale": 0}),
                ("/api/character", {"name": character_name, "world": world, "version": 220, "subversion": 0, "locale": 0}),
                # v1 API versions
                ("/api/v1/profiles/{name}", {"world": world, "version": 220, "subversion": 0, "locale": 0}),
                ("/api/v1/characters/{name}", {"world": world, "version": 220, "subversion": 0, "locale": 0}),
                ("/api/v1/character/{name}", {"world": world, "version": 220, "subversion": 0, "locale": 0}),
                # Without /api prefix
                ("/profiles/{name}", {"world": world, "version": 220, "subversion": 0, "locale": 0}),
                ("/characters/{name}", {"world": world, "version": 220, "subversion": 0, "locale": 0}),
                ("/character/{name}", {"world": world, "version": 220, "subversion": 0, "locale": 0}),
                # Digits-specific endpoints (maplestory.net/digits feature)
                ("/api/digits/character/{name}", {"world": world, "version": 220, "subversion": 0, "locale": 0}),
                ("/digits/api/character/{name}", {"world": world, "version": 220, "subversion": 0, "locale": 0}),
                # Also try without version params (API might default to GMS)
                ("/api/profiles/{name}", {"world": world}),
                ("/api/characters/{name}", {"world": world}),
                ("/api/character/{name}", {"world": world}),
                ("/api/characters", {"name": character_name, "world": world}),
            ]
            
            # Also try with token as query parameter
            auth_variants = [
                ("header", headers, {}),
                ("query", {k: v for k, v in headers.items() if k != "Authorization"}, {"token": self.access_token, "access_token": self.access_token, "api_key": self.access_token}),
            ]
            
            for base_url in MAPLESTORY_NETWORK_API_BASE_OPTIONS:
                for auth_method, req_headers, auth_params in auth_variants:
                    for endpoint_template, params in endpoint_formats:
                        try:
                            if "{name}" in endpoint_template:
                                url = f"{base_url}{endpoint_template.format(name=character_name)}"
                            else:
                                url = f"{base_url}{endpoint_template}"
                            
                            # Merge auth params with regular params
                            all_params = {**params, **auth_params}
                            
                            # #region agent log
                            try:
                                with open("/app/debug.log", "a", encoding="utf-8") as f:
                                    f.write(json.dumps({"sessionId":"debug-session","runId":"run3","hypothesisId":"Q","location":"maplestory_network_api.py:110","message":"Trying API endpoint with auth variant","data":{"base_url":base_url,"endpoint":endpoint_template,"url":url,"params":all_params,"auth_method":auth_method},"timestamp":int(__import__("time").time()*1000)})+"\n")
                            except Exception:
                                pass
                            # #endregion
                            
                            response = await client.get(url, params=all_params, headers=req_headers, follow_redirects=True)
                            
                            # #region agent log
                            try:
                                with open("/app/debug.log", "a", encoding="utf-8") as f:
                                    try:
                                        resp_text = response.text[:1000] if hasattr(response, 'text') and response.text else (str(response.content[:1000]) if hasattr(response, 'content') else "no response body")
                                        resp_headers = dict(response.headers) if hasattr(response, 'headers') else {}
                                    except Exception as ex:
                                        resp_text = f"unable to read response: {ex}"
                                        resp_headers = {}
                                    f.write(json.dumps({"sessionId":"debug-session","runId":"run3","hypothesisId":"K","location":"maplestory_network_api.py:148","message":"API response","data":{"status_code":response.status_code,"url":str(response.url),"response_body":resp_text,"response_headers":resp_headers},"timestamp":int(__import__("time").time()*1000)})+"\n")
                            except Exception:
                                pass
                            # #endregion
                            
                            if response.status_code == 200:
                                # Success! Parse and return
                                data = response.json()
                                
                                # #region agent log
                                try:
                                    with open("/app/debug.log", "a", encoding="utf-8") as f:
                                        f.write(json.dumps({"sessionId":"debug-session","runId":"run3","hypothesisId":"L","location":"maplestory_network_api.py:165","message":"Success! Found working endpoint","data":{"base_url":base_url,"endpoint":endpoint_template,"data_keys":list(data.keys()) if isinstance(data, dict) else "not_dict"},"timestamp":int(__import__("time").time()*1000)})+"\n")
                                except Exception:
                                    pass
                                # #endregion
                                
                                # Map response to our expected format
                                result = {
                                    "character_name": data.get("name") or data.get("character_name") or character_name,
                                    "world": data.get("world") or data.get("world_name") or world,
                                    "world_name": data.get("world") or data.get("world_name") or world,
                                    "level": data.get("level") or data.get("character_level"),
                                    "character_level": data.get("level") or data.get("character_level"),
                                    "job": data.get("job") or data.get("character_class") or data.get("class"),
                                    "character_class": data.get("job") or data.get("character_class") or data.get("class"),
                                    "character_image": data.get("character_image") or data.get("image_url") or data.get("avatar_url"),
                                    "character_icon_url": data.get("character_image") or data.get("image_url") or data.get("avatar_url"),
                                    "ocid": data.get("ocid") or data.get("id"),
                                    "nexon_ocid": None,
                                }
                                return result
                            elif response.status_code != 404:
                                # Non-404 error, might be auth or other issue
                                last_error = f"Status {response.status_code}: {response.text[:200] if hasattr(response, 'text') else 'unknown'}"
                        except httpx.HTTPStatusError as e:
                            # #region agent log
                            try:
                                with open("/app/debug.log", "a", encoding="utf-8") as f:
                                    try:
                                        error_body = e.response.text[:1000] if hasattr(e.response, 'text') and e.response.text else (str(e.response.content[:1000]) if hasattr(e.response, 'content') else "no error body")
                                    except Exception:
                                        error_body = "unable to read error"
                                    f.write(json.dumps({"sessionId":"debug-session","runId":"run3","hypothesisId":"M","location":"maplestory_network_api.py:193","message":"HTTPStatusError for endpoint","data":{"status_code":e.response.status_code,"url":str(e.response.url),"error_body":error_body},"timestamp":int(__import__("time").time()*1000)})+"\n")
                            except Exception:
                                pass
                            # #endregion
                            
                            if e.response.status_code == 200:
                                # Should have been caught above, but just in case
                                data = e.response.json()
                                result = {
                                    "character_name": data.get("name") or data.get("character_name") or character_name,
                                    "world": data.get("world") or data.get("world_name") or world,
                                    "world_name": data.get("world") or data.get("world_name") or world,
                                    "level": data.get("level") or data.get("character_level"),
                                    "character_level": data.get("level") or data.get("character_level"),
                                    "job": data.get("job") or data.get("character_class") or data.get("class"),
                                    "character_class": data.get("job") or data.get("character_class") or data.get("class"),
                                    "character_image": data.get("character_image") or data.get("image_url") or data.get("avatar_url"),
                                    "character_icon_url": data.get("character_image") or data.get("image_url") or data.get("avatar_url"),
                                    "ocid": data.get("ocid") or data.get("id"),
                                    "nexon_ocid": None,
                                }
                                return result
                            elif e.response.status_code != 404:
                                last_error = f"Status {e.response.status_code}: {e.response.text[:200] if hasattr(e.response, 'text') else 'unknown'}"
                        except Exception as ex:
                            # #region agent log
                            try:
                                with open("/app/debug.log", "a", encoding="utf-8") as f:
                                    f.write(json.dumps({"sessionId":"debug-session","runId":"run3","hypothesisId":"N","location":"maplestory_network_api.py:223","message":"Exception during API call","data":{"error_type":type(ex).__name__,"error_str":str(ex)},"timestamp":int(__import__("time").time()*1000)})+"\n")
                            except Exception:
                                pass
                            # #endregion
                            continue
            
            # If we get here, all endpoints returned 404 or errors
            # Final attempt - check if we got any non-404 errors
            if last_error:
                raise MapleStoryNetworkAPIError(f"MapleStory Network API error: {last_error}")
            else:
                raise MapleStoryNetworkAPIError(f"Character '{character_name}' on {world} not found (tried all endpoint formats)")


def get_maplestory_network_client() -> Optional[MapleStoryNetworkAPIClient]:
    """Get MapleStory Network API client if token is configured."""
    try:
        return MapleStoryNetworkAPIClient()
    except MapleStoryNetworkAPIError:
        return None

