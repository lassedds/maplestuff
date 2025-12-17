# No-Login Mode (Temporary)

This document explains the temporary no-login mode that has been enabled for easier development and testing.

## How It Works

### Backend
- When `DEBUG=true` in backend `.env`, the backend automatically creates/uses a mock user
- All endpoints that require authentication will use this mock user instead of requiring Discord OAuth
- No Redis or Discord OAuth setup is required in this mode

### Frontend
- The login page automatically redirects to the dashboard
- All pages work without requiring authentication
- Character management and other features work with the mock user

## Configuration

### Backend (.env)
```env
DEBUG=true
```

That's it! No need for:
- `DISCORD_CLIENT_ID`
- `DISCORD_CLIENT_SECRET`
- `REDIS_URL` (optional, but recommended for sessions)

### Frontend
No changes needed - it automatically works without login.

## MapleStory.io API Integration

The MapleStory.io API has been integrated for fetching item sprites and game data:

### Backend Endpoints
- `GET /api/maplestory/item/{item_id}/sprite-url` - Get item sprite URL
- `GET /api/maplestory/item/{item_id}/sprite` - Redirect to item sprite
- `GET /api/maplestory/item/{item_id}/info` - Get item information

### Frontend Usage
```typescript
import { MapleStoryAPI } from '@/services/maplestory';

// Get item sprite URL
const spriteUrl = MapleStoryAPI.getItemSpriteUrl(12345, 'GMS', 'latest', 64);

// Or use direct URL (bypasses backend)
const directUrl = MapleStoryAPI.getItemSpriteUrlDirect(12345, 'GMS', 'latest', 64);
```

## Re-enabling Login

To re-enable Discord OAuth login:

1. Set `DEBUG=false` in backend `.env`
2. Add Discord OAuth credentials:
   ```env
   DISCORD_CLIENT_ID=your_client_id
   DISCORD_CLIENT_SECRET=your_client_secret
   DISCORD_REDIRECT_URI=http://localhost:8000/api/auth/discord/callback
   ```
3. Update frontend `src/app/page.tsx` to show login button again
4. Update frontend pages to handle authentication errors properly

## Notes

- This is a **temporary** setup for development
- The mock user is shared across all requests when `DEBUG=true`
- Character data created in this mode will be associated with the mock user
- When switching back to real auth, you may want to clean up mock user data


