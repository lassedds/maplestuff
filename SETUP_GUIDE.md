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
**When needed:** Step 6+ (Auth implementation)

**Detailed Setup Steps:**

1. **Go to Discord Developer Portal**
   - Visit: https://discord.com/developers/applications
   - Log in with your Discord account

2. **Create New Application**
   - Click "New Application" button (top right)
   - Name it "GMSTracker" (or your preferred name)
   - Accept the Terms of Service
   - Click "Create"

3. **Get Client ID**
   - You're now on the application page
   - Under "General Information" tab
   - Copy the "Application ID" - this is your `DISCORD_CLIENT_ID`

4. **Get Client Secret**
   - Go to "OAuth2" → "General" in the left sidebar
   - Under "Client Secret", click "Reset Secret"
   - Copy the secret - this is your `DISCORD_CLIENT_SECRET`
   - ⚠️ **Save this immediately** - you can't see it again!

5. **Configure Redirect URI**
   - Still in "OAuth2" → "General"
   - Under "Redirects", click "Add Redirect"
   - For local development, add: `http://localhost:8000/api/auth/discord/callback`
   - For production, add your actual domain
   - Click "Save Changes"

**What to provide:**
```
DISCORD_CLIENT_ID=your_application_id_here
DISCORD_CLIENT_SECRET=your_client_secret_here
DISCORD_REDIRECT_URI=http://localhost:8000/api/auth/discord/callback
```

**Auth Flow:**
```
User clicks "Login with Discord"
    ↓
GET /api/auth/discord → Redirects to Discord
    ↓
User authorizes on Discord
    ↓
Discord redirects to /api/auth/discord/callback
    ↓
Backend exchanges code for token, creates session
    ↓
User redirected to frontend with session cookie
```

**Scopes used:** `identify` (just basic user info - no access to servers, messages, etc.)

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

## Quick Start with Docker (Recommended)

### One-Command Setup

```bash
# 1. Copy and edit environment file
cp .env.example .env
# Edit .env and add your Discord credentials

# 2. Start everything
docker-compose up
```

This starts:
- PostgreSQL on port 5432
- Redis on port 6379
- Backend API on http://localhost:8000
- Frontend on http://localhost:3000

The backend will automatically:
- Run database migrations
- Seed boss/item data
- Start the API server

### Manual Setup (Without Docker)

```bash
# Start PostgreSQL and Redis manually or via Docker
docker-compose up -d db redis

# Backend setup
cd backend
pip install -r requirements.txt
alembic upgrade head
python -m app.seeds.seed_db
uvicorn app.main:app --reload

# Frontend setup (in another terminal)
cd frontend
npm install
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
