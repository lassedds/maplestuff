"""
Nexon MapleStory Rankings Scraper
Scrapes character data from https://www.nexon.com/maplestory/rankings

WARNING: This scraper should be used responsibly:
- Respect rate limits (add delays between requests)
- Check Nexon's Terms of Service before using
- Consider using official APIs when available
- This is a fallback option when APIs are unavailable
"""

import httpx
import json
import re
from typing import Optional, Dict
from urllib.parse import quote
import os
from datetime import datetime

from app.config import settings


class NexonRankingsScraperError(Exception):
    """Error when scraping Nexon rankings."""
    pass


class NexonRankingsScraper:
    """
    Scraper for Nexon MapleStory rankings page.
    Attempts to find and use API endpoints first, falls back to HTML parsing.
    """

    def __init__(self):
        self.base_url = "https://www.nexon.com"
        self.rankings_url = f"{self.base_url}/maplestory/rankings"
        self.client = httpx.AsyncClient(
            timeout=15.0,
            follow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": f"{self.base_url}/maplestory/",
            }
        )
        
        # World to region mapping
        # NA (North America): Scania, Bera (regular), Kronos, Hyperion (reboot)
        # EU (Europe): Luna (regular), Solis (reboot)
        self.world_to_region = {
            # North America (GMS)
            "scania": "na",
            "bera": "na",
            "kronos": "na",
            "hyperion": "na",
            # Europe (EMS)
            "solis": "eu",
            "luna": "eu",
        }
        
        # WorldID to world name mapping
        # These IDs are used by the Nexon rankings API
        self.world_id_to_name = {
            # NA Regular servers
            19: "Scania",
            1: "Bera",
            # NA Reboot servers
            45: "Kronos",  # Reboot NA
            70: "Hyperion",  # Reboot NA
            # EU Regular servers
            30: "Luna",
            # EU Reboot servers
            46: "Solis",  # Reboot EU
        }

    def _is_reboot_world(self, world: str) -> bool:
        """Check if world is a Reboot world."""
        world_lower = world.lower()
        # Reboot worlds: Kronos, Hyperion (NA), Solis (EU)
        reboot_worlds = {"kronos", "hyperion", "solis"}
        return world_lower in reboot_worlds
    
    def _get_region_from_world(self, world: str) -> str:
        """Get region code (na, eu) from world name."""
        world_lower = world.lower()
        return self.world_to_region.get(world_lower, "na")  # Default to NA
    
    async def _try_public_rankings_api(self, character_name: str, world: str) -> Optional[Dict]:
        """
        Try the public Nexon rankings API endpoint.
        Format: 
        - Regular servers: /api/maplestory/no-auth/ranking/v2/{region}?type=overall&id=weekly&regular_index=1&page_index=1&character_name={name}
        - Reboot servers: /api/maplestory/no-auth/ranking/v2/{region}?type=overall&id=weekly&reboot_index=1&page_index=1&character_name={name}
        """
        # #region agent log
        log_path = "/app/.cursor/debug.log"
        try:
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"nexon_rankings_scraper.py:_try_public_rankings_api:entry","message":"API lookup started","data":{"character_name":character_name,"world":world},"timestamp":int(datetime.now().timestamp()*1000)})+"\n")
        except: pass
        # #endregion
        
        region = self._get_region_from_world(world)
        is_reboot = self._is_reboot_world(world)
        
        # #region agent log
        log_path = "/app/.cursor/debug.log"
        try:
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"E","location":"nexon_rankings_scraper.py:_try_public_rankings_api:params","message":"Region and reboot detection","data":{"region":region,"is_reboot":is_reboot,"world_lower":world.lower()},"timestamp":int(datetime.now().timestamp()*1000)})+"\n")
        except: pass
        # #endregion
        
        # Try both regular and reboot for the character (prefer the detected type first)
        attempts = []
        if is_reboot:
            attempts.append({"reboot_index": 1})
            attempts.append({"regular_index": 1})  # Fallback to regular
        else:
            attempts.append({"regular_index": 1})
            attempts.append({"reboot_index": 1})  # Fallback to reboot
        
        for params_variant in attempts:
            try:
                endpoint = f"{self.base_url}/api/maplestory/no-auth/ranking/v2/{region}"
                params = {
                    "type": "overall",
                    "id": "weekly",
                    "page_index": 1,
                    "character_name": character_name,
                    **params_variant,  # Add either regular_index=1 or reboot_index=1
                }
                
                # #region agent log
                log_path = "/app/.cursor/debug.log"
                try:
                    os.makedirs(os.path.dirname(log_path), exist_ok=True)
                    with open(log_path, "a", encoding="utf-8") as f:
                        f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"nexon_rankings_scraper.py:_try_public_rankings_api:request","message":"Making API request","data":{"endpoint":endpoint,"params":params},"timestamp":int(datetime.now().timestamp()*1000)})+"\n")
                except: pass
                # #endregion
                
                response = await self.client.get(endpoint, params=params)
                
                # #region agent log
                log_path = "/app/.cursor/debug.log"
                try:
                    os.makedirs(os.path.dirname(log_path), exist_ok=True)
                    with open(log_path, "a", encoding="utf-8") as f:
                        f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"nexon_rankings_scraper.py:_try_public_rankings_api:response","message":"API response received","data":{"status_code":response.status_code,"has_content":bool(response.content)},"timestamp":int(datetime.now().timestamp()*1000)})+"\n")
                except: pass
                # #endregion
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        
                        # #region agent log
                        log_path = "/app/.cursor/debug.log"
                        try:
                            os.makedirs(os.path.dirname(log_path), exist_ok=True)
                            with open(log_path, "a", encoding="utf-8") as f:
                                f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"B","location":"nexon_rankings_scraper.py:_try_public_rankings_api:parsed","message":"Response parsed","data":{"is_dict":isinstance(data,dict),"has_ranks":"ranks" in data if isinstance(data,dict) else False,"totalCount":data.get("totalCount") if isinstance(data,dict) else None},"timestamp":int(datetime.now().timestamp()*1000)})+"\n")
                        except: pass
                        # #endregion
                        
                        # Check if response has the expected format with ranks array
                        if isinstance(data, dict) and "ranks" in data:
                            ranks = data.get("ranks", [])
                            
                            # #region agent log
                            log_path = "/app/.cursor/debug.log"
                            try:
                                os.makedirs(os.path.dirname(log_path), exist_ok=True)
                                with open(log_path, "a", encoding="utf-8") as f:
                                    f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"B","location":"nexon_rankings_scraper.py:_try_public_rankings_api:ranks","message":"Ranks array check","data":{"ranks_count":len(ranks),"ranks_sample":[{"name":r.get("characterName"),"worldID":r.get("worldID")} for r in ranks[:3]] if ranks else []},"timestamp":int(datetime.now().timestamp()*1000)})+"\n")
                            except: pass
                            # #endregion
                            
                            if ranks:
                                # Find the character in the ranks (should match character_name)
                                for rank_entry in ranks:
                                    rank_name = rank_entry.get("characterName", "").lower()
                                    
                                    # #region agent log
                                    log_path = "/app/.cursor/debug.log"
                                    try:
                                        os.makedirs(os.path.dirname(log_path), exist_ok=True)
                                        with open(log_path, "a", encoding="utf-8") as f:
                                            f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"C","location":"nexon_rankings_scraper.py:_try_public_rankings_api:match","message":"Checking character name match","data":{"rank_name":rank_name,"search_name":character_name.lower(),"matches":rank_name==character_name.lower()},"timestamp":int(datetime.now().timestamp()*1000)})+"\n")
                                    except: pass
                                    # #endregion
                                    
                                    if rank_name == character_name.lower():
                                        result = self._parse_rankings_api_response(rank_entry, world)
                                        
                                        # #region agent log
                                        log_path = "/app/.cursor/debug.log"
                                        try:
                                            os.makedirs(os.path.dirname(log_path), exist_ok=True)
                                            with open(log_path, "a", encoding="utf-8") as f:
                                                f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"nexon_rankings_scraper.py:_try_public_rankings_api:success","message":"Character found and parsed","data":{"result_world":result.get("world"),"result_level":result.get("level")},"timestamp":int(datetime.now().timestamp()*1000)})+"\n")
                                        except: pass
                                        # #endregion
                                        
                                        return result
                    except json.JSONDecodeError as e:
                        # #region agent log
                        log_path = "/app/.cursor/debug.log"
                        try:
                            os.makedirs(os.path.dirname(log_path), exist_ok=True)
                            with open(log_path, "a", encoding="utf-8") as f:
                                f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"B","location":"nexon_rankings_scraper.py:_try_public_rankings_api:json_error","message":"JSON decode error","data":{"error":str(e)},"timestamp":int(datetime.now().timestamp()*1000)})+"\n")
                        except: pass
                        # #endregion
                        continue
            except Exception as e:
                # #region agent log
                log_path = "/app/.cursor/debug.log"
                try:
                    os.makedirs(os.path.dirname(log_path), exist_ok=True)
                    with open(log_path, "a", encoding="utf-8") as f:
                        f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"nexon_rankings_scraper.py:_try_public_rankings_api:exception","message":"Exception during API call","data":{"error":str(e),"error_type":type(e).__name__},"timestamp":int(datetime.now().timestamp()*1000)})+"\n")
                except: pass
                # #endregion
                continue
        
        # #region agent log
        log_path = "/app/.cursor/debug.log"
        try:
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"nexon_rankings_scraper.py:_try_public_rankings_api:exit","message":"No character found in API","data":{},"timestamp":int(datetime.now().timestamp()*1000)})+"\n")
        except: pass
        # #endregion
        
        return None
    
    async def _try_api_endpoint(self, character_name: str, world: str) -> Optional[Dict]:
        """
        Try to find and use the API endpoint that the rankings page uses.
        Many modern websites load data via API calls that we can use directly.
        """
        # First, try the public rankings API (preferred)
        public_api_result = await self._try_public_rankings_api(character_name, world)
        if public_api_result:
            return public_api_result
        
        # Fallback to other API endpoint patterns
        api_endpoints = [
            f"{self.base_url}/api/maplestory/rankings/character",
            f"{self.base_url}/api/maplestory/character",
            f"{self.base_url}/maplestory/api/rankings/character",
            f"{self.base_url}/maplestory/api/character",
            f"{self.base_url}/api/v1/maplestory/character",
        ]
        
        params_variants = [
            {"characterName": character_name, "world": world},
            {"name": character_name, "world": world},
            {"character_name": character_name, "world": world},
            {"characterName": character_name, "worldName": world},
        ]
        
        for endpoint in api_endpoints:
            for params in params_variants:
                try:
                    response = await self.client.get(endpoint, params=params)
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            # Check if response looks like character data
                            if isinstance(data, dict) and any(key in data for key in ["characterName", "name", "level", "job"]):
                                return self._parse_api_response(data, character_name, world)
                        except json.JSONDecodeError:
                            continue
                except Exception:
                    continue
        
        return None

    async def _fetch_rankings_page(self, character_name: str, world: str) -> str:
        """
        Fetch the rankings page, possibly with search parameters.
        """
        # Try different URL patterns for character search
        search_urls = [
            f"{self.rankings_url}?characterName={quote(character_name)}&world={quote(world)}",
            f"{self.rankings_url}?name={quote(character_name)}&world={quote(world)}",
            f"{self.rankings_url}?search={quote(character_name)}&world={quote(world)}",
            self.rankings_url,  # Fallback to base rankings page
        ]
        
        for url in search_urls:
            try:
                response = await self.client.get(url)
                if response.status_code == 200:
                    return response.text
            except Exception:
                continue
        
        raise NexonRankingsScraperError(f"Failed to fetch rankings page")

    def _parse_html_response(self, html: str, character_name: str, world: str) -> Dict:
        """
        Parse HTML response to extract character data.
        This is a fallback when API endpoints aren't available.
        """
        # Try to find JSON data embedded in the page (many React apps do this)
        json_patterns = [
            r'window\.__INITIAL_STATE__\s*=\s*({.+?});',
            r'window\.__NEXT_DATA__\s*=\s*({.+?});',
            r'<script[^>]*id="__NEXT_DATA__"[^>]*>({.+?})</script>',
            r'"characterData"\s*:\s*({.+?})',
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, html, re.DOTALL)
            for match in matches:
                try:
                    data = json.loads(match)
                    parsed = self._extract_character_from_json(data, character_name, world)
                    if parsed:
                        return parsed
                except (json.JSONDecodeError, KeyError):
                    continue
        
        # Fallback: Try to parse HTML directly (more fragile)
        # Look for character name, level, job in the HTML
        level_match = re.search(rf'{re.escape(character_name)}.*?Level[:\s]+(\d+)', html, re.IGNORECASE)
        job_match = re.search(rf'{re.escape(character_name)}.*?(?:Job|Class)[:\s]+([A-Za-z\s]+)', html, re.IGNORECASE)
        
        result = {
            "character_name": character_name,
            "world": world,
            "world_name": world,
            "level": int(level_match.group(1)) if level_match else None,
            "character_level": int(level_match.group(1)) if level_match else None,
            "job": job_match.group(1).strip() if job_match else None,
            "character_class": job_match.group(1).strip() if job_match else None,
            "character_image": None,
            "character_icon_url": None,
            "ocid": None,
            "nexon_ocid": None,
        }
        
        if not result["level"]:
            raise NexonRankingsScraperError(f"Character '{character_name}' on {world} not found in rankings")
        
        return result

    def _extract_character_from_json(self, data: Dict, character_name: str, world: str) -> Optional[Dict]:
        """
        Recursively search JSON data for character information.
        """
        def find_character(obj, path=""):
            if isinstance(obj, dict):
                # Check if this looks like character data
                name = obj.get("characterName") or obj.get("name") or obj.get("character_name")
                if name and name.lower() == character_name.lower():
                    world_name = obj.get("world") or obj.get("worldName") or obj.get("world_name")
                    if world_name and world_name.lower() == world.lower():
                        return {
                            "character_name": name,
                            "world": world_name,
                            "world_name": world_name,
                            "level": obj.get("level") or obj.get("characterLevel") or obj.get("character_level"),
                            "character_level": obj.get("level") or obj.get("characterLevel") or obj.get("character_level"),
                            "job": obj.get("job") or obj.get("characterClass") or obj.get("character_class") or obj.get("class"),
                            "character_class": obj.get("job") or obj.get("characterClass") or obj.get("character_class") or obj.get("class"),
                            "character_image": obj.get("characterImage") or obj.get("image") or obj.get("imageUrl"),
                            "character_icon_url": obj.get("characterImage") or obj.get("image") or obj.get("imageUrl"),
                            "ocid": obj.get("ocid") or obj.get("id"),
                            "nexon_ocid": obj.get("ocid") or obj.get("id"),
                            # Total experience when present
                            "exp": obj.get("exp") or obj.get("experience") or obj.get("totalExp"),
                        }
                # Recursively search nested objects
                for key, value in obj.items():
                    result = find_character(value, f"{path}.{key}")
                    if result:
                        return result
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    result = find_character(item, f"{path}[{i}]")
                    if result:
                        return result
            return None
        
        return find_character(data)

    def _get_world_name_from_id(self, world_id: int) -> Optional[str]:
        """Get world name from worldID."""
        result = self.world_id_to_name.get(world_id)
        
        # #region agent log
        log_path = "/app/.cursor/debug.log"
        try:
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"D","location":"nexon_rankings_scraper.py:_get_world_name_from_id","message":"WorldID mapping lookup","data":{"world_id":world_id,"mapped_name":result,"available_ids":list(self.world_id_to_name.keys())},"timestamp":int(datetime.now().timestamp()*1000)})+"\n")
        except: pass
        # #endregion
        
        return result
    
    def _parse_rankings_api_response(self, rank_entry: Dict, world: str) -> Dict:
        """
        Parse the public rankings API response format.
        Format: {"characterName": "...", "level": 285, "jobName": "Zero", "characterImgURL": "...", "worldID": 46, ...}
        """
        # #region agent log
        log_path = "/app/.cursor/debug.log"
        try:
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"D","location":"nexon_rankings_scraper.py:_parse_rankings_api_response:entry","message":"Parsing API response","data":{"rank_entry_keys":list(rank_entry.keys()),"worldID":rank_entry.get("worldID"),"characterName":rank_entry.get("characterName")},"timestamp":int(datetime.now().timestamp()*1000)})+"\n")
        except: pass
        # #endregion
        
        character_id = rank_entry.get("characterID")
        # characterID of 0 means it's not available/valid
        ocid = str(character_id) if character_id and character_id != 0 else None
        
        # Get world name from worldID if available, otherwise use provided world
        world_id = rank_entry.get("worldID")
        actual_world = self._get_world_name_from_id(world_id) if world_id is not None else world
        
        # #region agent log
        log_path = "/app/.cursor/debug.log"
        try:
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"D","location":"nexon_rankings_scraper.py:_parse_rankings_api_response:mapped","message":"World mapped from worldID","data":{"world_id":world_id,"actual_world":actual_world,"fallback_world":world},"timestamp":int(datetime.now().timestamp()*1000)})+"\n")
        except: pass
        # #endregion
        
        result = {
            "character_name": rank_entry.get("characterName") or "",
            "world": actual_world,
            "level": rank_entry.get("level"),
            "job": rank_entry.get("jobName") or rank_entry.get("job"),
            "character_image": rank_entry.get("characterImgURL"),
            "character_icon_url": rank_entry.get("characterImgURL"),
            "nexon_ocid": ocid,
            "exp": rank_entry.get("exp"),  # Total XP from rankings API
        }
        
        # #region agent log
        log_path = "/app/.cursor/debug.log"
        try:
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"D","location":"nexon_rankings_scraper.py:_parse_rankings_api_response:exit","message":"Parsed result","data":{"result_world":result.get("world"),"result_level":result.get("level"),"result_job":result.get("job")},"timestamp":int(datetime.now().timestamp()*1000)})+"\n")
        except: pass
        # #endregion
        
        return result
    
    def _parse_api_response(self, data: Dict, character_name: str, world: str) -> Dict:
        """
        Parse API response into our standard format.
        """
        return {
            "character_name": data.get("characterName") or data.get("name") or character_name,
            "world": data.get("world") or data.get("worldName") or world,
            "world_name": data.get("world") or data.get("worldName") or world,
            "level": data.get("level") or data.get("characterLevel") or data.get("character_level"),
            "character_level": data.get("level") or data.get("characterLevel") or data.get("character_level"),
            "job": data.get("job") or data.get("characterClass") or data.get("character_class") or data.get("class"),
            "character_class": data.get("job") or data.get("characterClass") or data.get("character_class") or data.get("class"),
            "character_image": data.get("characterImage") or data.get("image") or data.get("imageUrl"),
            "character_icon_url": data.get("characterImage") or data.get("image") or data.get("imageUrl"),
            "ocid": data.get("ocid") or data.get("id"),
            "nexon_ocid": data.get("ocid") or data.get("id"),
            # Total experience when provided by the rankings API/schema
            "exp": data.get("exp") or data.get("experience") or data.get("totalExp"),
        }

    async def lookup_character(self, character_name: str, world: str) -> Dict:
        """
        Look up character data from Nexon rankings page.
        
        Args:
            character_name: Character name
            world: World/server name (e.g., "Scania", "Bera", "Kronos")
        
        Returns:
            Dictionary with character data
        
        Raises:
            NexonRankingsScraperError: If lookup fails
        """
        # #region agent log
        log_path = "/app/.cursor/debug.log"
        try:
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"nexon_rankings_scraper.py:lookup_character:entry","message":"Character lookup started","data":{"character_name":character_name,"world":world},"timestamp":int(datetime.now().timestamp()*1000)})+"\n")
        except: pass
        # #endregion
        
        # First, try to find and use API endpoints (preferred method)
        api_result = await self._try_api_endpoint(character_name, world)
        
        # #region agent log
        log_path = "/app/.cursor/debug.log"
        try:
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"nexon_rankings_scraper.py:lookup_character:api_result","message":"API endpoint result","data":{"has_result":api_result is not None,"result_keys":list(api_result.keys()) if api_result else []},"timestamp":int(datetime.now().timestamp()*1000)})+"\n")
        except: pass
        # #endregion
        
        if api_result:
            return api_result
        
        # #region agent log
        log_path = "/app/.cursor/debug.log"
        try:
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"nexon_rankings_scraper.py:lookup_character:fallback","message":"Falling back to HTML scraping","data":{},"timestamp":int(datetime.now().timestamp()*1000)})+"\n")
        except: pass
        # #endregion
        
        # Fallback to HTML scraping
        html = await self._fetch_rankings_page(character_name, world)
        return self._parse_html_response(html, character_name, world)

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


def get_nexon_rankings_scraper() -> Optional[NexonRankingsScraper]:
    """Get Nexon rankings scraper instance."""
    try:
        return NexonRankingsScraper()
    except Exception:
        return None
