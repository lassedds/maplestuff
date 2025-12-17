# MapleStory GMS API Research Summary

## Research Findings

Based on extensive research, here's what we found about how websites track GMS MapleStory players:

### Available APIs

1. **MapleStory Network API (maplestory.net)**
   - **Status**: Community-driven API for GMS
   - **Authentication**: OAuth JWT tokens (you have one)
   - **Documentation**: https://maplestory.net/develop/
   - **GMS Defaults**: `version=220, subversion=0, locale=0`
   - **Issue**: Public endpoint structure not fully documented
   - **Features**: Character data, rankings, equipment, historical data

2. **MapleStory Universe Open API (msu.io)**
   - **Status**: Official Nexon API (v1rc1)
   - **Access**: Requires API key application
   - **Documentation**: https://msu.io/builder/docs
   - **Features**: Wallet data, character stats, in-game metadata, token-level items

3. **NEXON Open API**
   - **Status**: Official API, but primarily for KMS, TMS, MSEA
   - **GMS Support**: Limited/Nonexistent
   - **Documentation**: https://openapi.nexon.com

4. **MapleStory.IO API**
   - **Status**: Free service for game assets
   - **Features**: Character rendering, items, mobs, quests
   - **Documentation**: https://maplestory.io
   - **Note**: More for assets than character tracking

### How Websites Track Players

Based on research, websites like:
- **maplestory.net/digits** - Uses MapleStory Network API
- **maplehub.app** - Likely uses MapleStory Network API or scraping
- **mapleranks.com** - Uses MapleStory Network API
- **devnayr.com** - Uses MapleStory Network API

All appear to use the **MapleStory Network API** which requires:
1. Registration at maplestory.net/develop
2. OAuth token (JWT) - which you have
3. Proper endpoint structure (not publicly documented)

### Current Implementation Status

We've implemented support for:
- ✅ Multiple base URLs (`api.maplestory.net`, `maplestory.net/api`, etc.)
- ✅ GraphQL endpoint attempts
- ✅ REST endpoint patterns (`/api/profiles/{name}`, `/api/characters/{name}`, etc.)
- ✅ Version parameters (`version=220, subversion=0, locale=0`)
- ✅ Multiple authentication methods (Bearer token in header, query params)
- ✅ Debug logging to `/app/debug.log`

### Next Steps

1. **Check Actual API Documentation**
   - Visit https://maplestory.net/develop/ while logged in
   - Look for actual endpoint documentation
   - Check if there's an API explorer or Swagger docs

2. **Inspect Network Requests**
   - Open browser DevTools on maplestory.net/digits
   - Search for a character (e.g., "ErekloEvan" on "Kronos")
   - Check Network tab to see actual API calls
   - Note the exact endpoint URLs and request format

3. **Contact MapleStory Network**
   - Email: [email protected] (mentioned in their docs)
   - Ask for API endpoint documentation
   - Request example requests/responses

4. **Alternative: Use maplestory.gg**
   - Research if maplestory.gg has a public API
   - Check their website structure
   - May require web scraping (not recommended but might be necessary)

5. **Check Debug Logs**
   - After testing, check `/app/debug.log` in the backend container
   - Look for any successful responses or error messages that reveal the API structure

### Testing

To test the current implementation:
1. Go to http://localhost:3000/characters
2. Enter character name: "ErekloEvan"
3. Enter world: "Kronos"
4. Click "🔍 Lookup Character"
5. Check backend logs: `docker-compose exec backend cat /app/debug.log | tail -100`

### Nexon Rankings Scraping (Fallback Option)

**Status**: ✅ Implemented as fallback

**Approach**:
1. **First**: Tries to find API endpoints that the rankings page uses (preferred - not really scraping)
2. **Fallback**: Parses HTML/JSON from the rankings page

**Implementation**:
- Created `backend/app/services/nexon_rankings_scraper.py`
- Integrated as fallback in character lookup endpoint
- Tries multiple API endpoint patterns first
- Falls back to HTML parsing if needed
- Extracts embedded JSON data from React/Next.js apps

**Legal Considerations**:
⚠️ **IMPORTANT**: 
- Check Nexon's Terms of Service before using
- Respect rate limits (add delays between requests)
- Use responsibly and ethically
- Consider this a temporary solution until official APIs are available
- Prefer official APIs when possible

**How It Works**:
1. Tries API endpoints like `/api/maplestory/character` first
2. If that fails, fetches the rankings page HTML
3. Extracts JSON data embedded in the page (React/Next.js apps often do this)
4. Falls back to HTML parsing if needed

**Usage**:
The scraper is automatically used as a fallback when MapleStory Network API fails. No configuration needed - it's always available as a fallback option.

### References

- MapleStory Network Develop: https://maplestory.net/develop/
- MapleStory Universe API: https://msu.io/builder/docs
- NEXON Open API: https://openapi.nexon.com
- MapleStory.IO: https://maplestory.io
- Nexon Rankings: https://www.nexon.com/maplestory/rankings

