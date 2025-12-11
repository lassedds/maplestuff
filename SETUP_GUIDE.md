# GMSTracker Setup Guide

This document tracks all external services, APIs, and credentials needed to run GMSTracker.

---

## Required Services

### 1. PostgreSQL Database
**Status:** Required for all features
**When needed:** Step 2+

You need a PostgreSQL database. Options:
- **Local:** Use Docker Compose (included in project)
- **Cloud:** Railway, Supabase, Neon, or any PostgreSQL provider

**What to provide:**
```
DATABASE_URL=postgresql://username:password@host:port/database_name
```

**Example (local Docker):**
```
DATABASE_URL=postgresql://gmstracker:devpassword@localhost:5432/gmstracker
```

---

### 2. Redis
**Status:** Required for sessions and caching
**When needed:** Step 5+

Used for:
- User session storage
- Rate limiting
- Background job queues

**What to provide:**
```
REDIS_URL=redis://host:port
```

**Example (local Docker):**
```
REDIS_URL=redis://localhost:6379
```

---

### 3. Discord OAuth Application
**Status:** Required for user authentication
**When needed:** Step 6-9 (Auth implementation)

**Setup steps:**
1. Go to https://discord.com/developers/applications
2. Click "New Application"
3. Name it (e.g., "GMSTracker")
4. Go to OAuth2 → General
5. Add redirect URI: `http://localhost:3000/api/auth/discord/callback`
6. Copy Client ID and Client Secret

**What to provide:**
```
DISCORD_CLIENT_ID=your_client_id_here
DISCORD_CLIENT_SECRET=your_client_secret_here
DISCORD_REDIRECT_URI=http://localhost:3000/api/auth/discord/callback
```

**Scopes needed:** `identify` (just basic user info)

---

## Optional Services

### 4. maplestory.io API
**Status:** Optional (for sprites/images)
**When needed:** Frontend development

Public API, no credentials needed. Used for:
- Character renders
- Item sprites
- Boss images

**Base URL:** `https://maplestory.io/api`

---

## Environment Variables Summary

Create a `.env` file in `backend/` with:

```env
# === REQUIRED ===

# Database (PostgreSQL)
DATABASE_URL=postgresql://gmstracker:devpassword@localhost:5432/gmstracker

# Redis
REDIS_URL=redis://localhost:6379

# Discord OAuth (get from Discord Developer Portal)
DISCORD_CLIENT_ID=
DISCORD_CLIENT_SECRET=
DISCORD_REDIRECT_URI=http://localhost:3000/api/auth/discord/callback

# App Security
SECRET_KEY=generate-a-random-32-char-string-here

# === OPTIONAL ===

# Debug mode (set to false in production)
DEBUG=true

# URLs
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000
```

---

## Quick Start with Docker

Once all credentials are set, run:

```bash
# Start PostgreSQL and Redis
docker-compose up -d db redis

# Run migrations
cd backend
alembic upgrade head

# Start backend
uvicorn app.main:app --reload

# In another terminal, start frontend
cd frontend
npm run dev
```

---

## Checklist Before Running

- [ ] PostgreSQL running and DATABASE_URL set
- [ ] Redis running and REDIS_URL set
- [ ] Discord OAuth app created
- [ ] DISCORD_CLIENT_ID set
- [ ] DISCORD_CLIENT_SECRET set
- [ ] DISCORD_REDIRECT_URI set (must match Discord app settings)
- [ ] SECRET_KEY set (random string, min 32 chars)
- [ ] Migrations applied (`alembic upgrade head`)

---

## Getting Credentials From Me

When you're ready to run the app, I'll need you to provide:

1. **Database connection string** (or confirm using Docker)
2. **Redis connection string** (or confirm using Docker)
3. **Discord OAuth credentials:**
   - Client ID
   - Client Secret
   - Redirect URI you configured

I will **never** store or remember these credentials between sessions.
