---
name: maplehub-oss
description: Development guide for MapleHub OSS - an open-source MapleStory companion app with boss tracking, drop diary, daily/weekly tasks, and crowdsourced community drop rate statistics. Use this skill when working on the MapleHub clone project, implementing boss trackers, drop logging systems, MapleStory tools, or any features related to this project.
---

# MapleHub OSS Development Guide

Open-source MapleStory companion with personal tracking that feeds into community-wide drop rate statistics.

## Project Vision

An open-source MapleStory companion app with two core purposes:

1. **Personal Tracking** — Boss runs, dailies, drop diary, meso income
2. **Community Statistics** — Aggregated anonymous drop rate data from all users

The killer feature: **Every drop logged by users contributes to crowdsourced drop rate statistics** that the community has never had access to before (Nexon doesn't publish this data).

---

## Tech Stack

| Component | Technology | Why |
|-----------|------------|-----|
| Backend | FastAPI (Python 3.11+) | Async, fast, auto-docs |
| Frontend | Next.js 14+ (React, TypeScript) | SSR, great DX |
| Database | PostgreSQL | Relational, good for aggregations |
| Cache | Redis | Sessions, rate limiting, job queue |
| Auth | Discord OAuth2 | Community already uses Discord |
| Jobs | APScheduler or Celery | Stats aggregation, resets |
| Hosting | Vercel + Railway | Free tiers, easy deploy |

---

## Project Structure

```
maplehub-oss/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI app entry
│   │   ├── config.py               # Environment config
│   │   ├── database.py             # DB connection
│   │   │
│   │   ├── models/                 # SQLAlchemy models
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── character.py
│   │   │   ├── boss.py
│   │   │   ├── item.py
│   │   │   ├── boss_run.py
│   │   │   ├── task.py
│   │   │   └── stats.py
│   │   │
│   │   ├── schemas/                # Pydantic schemas
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── character.py
│   │   │   ├── boss.py
│   │   │   ├── tracking.py
│   │   │   ├── task.py
│   │   │   └── stats.py
│   │   │
│   │   ├── routers/                # API routes
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── characters.py
│   │   │   ├── bosses.py
│   │   │   ├── tracking.py         # Boss runs + drops
│   │   │   ├── tasks.py
│   │   │   ├── stats.py            # Public community stats
│   │   │   └── calculators.py
│   │   │
│   │   ├── services/               # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── discord_oauth.py
│   │   │   ├── boss_tracking.py
│   │   │   ├── drop_recording.py
│   │   │   ├── stats_aggregation.py
│   │   │   └── reset_times.py
│   │   │
│   │   └── jobs/                   # Background tasks
│   │       ├── __init__.py
│   │       ├── aggregate_stats.py
│   │       └── reset_periods.py
│   │
│   ├── seeds/                      # Seed data (JSON)
│   │   ├── bosses.json
│   │   ├── items.json
│   │   ├── boss_drop_tables.json
│   │   └── task_templates.json
│   │
│   ├── alembic/                    # DB migrations
│   │   ├── versions/
│   │   ├── env.py
│   │   └── alembic.ini
│   │
│   ├── tests/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   │   ├── Header.tsx
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   └── Layout.tsx
│   │   │   ├── boss-tracker/
│   │   │   │   ├── BossGrid.tsx
│   │   │   │   ├── BossCard.tsx
│   │   │   │   └── LogRunModal.tsx
│   │   │   ├── drop-diary/
│   │   │   │   ├── DropSelector.tsx
│   │   │   │   ├── ItemSearch.tsx
│   │   │   │   └── RunHistory.tsx
│   │   │   ├── stats/
│   │   │   │   ├── DropRateTable.tsx
│   │   │   │   └── TrendChart.tsx
│   │   │   └── tasks/
│   │   │       ├── TaskList.tsx
│   │   │       └── TaskItem.tsx
│   │   │
│   │   ├── pages/                  # or app/ for App Router
│   │   │   ├── index.tsx
│   │   │   ├── dashboard.tsx
│   │   │   ├── bosses.tsx
│   │   │   ├── diary.tsx           # Personal drop history
│   │   │   ├── stats.tsx           # Community statistics
│   │   │   ├── tasks.tsx
│   │   │   └── calculators/
│   │   │       ├── liberation.tsx
│   │   │       └── symbols.tsx
│   │   │
│   │   ├── hooks/
│   │   │   ├── useAuth.ts
│   │   │   ├── useCharacters.ts
│   │   │   ├── useBossTracking.ts
│   │   │   └── useDropRates.ts
│   │   │
│   │   ├── services/
│   │   │   └── api.ts              # API client
│   │   │
│   │   ├── types/
│   │   │   └── index.ts
│   │   │
│   │   └── utils/
│   │       └── resetTimes.ts
│   │
│   ├── public/
│   │   └── images/
│   │       ├── bosses/
│   │       └── items/
│   │
│   ├── package.json
│   ├── tailwind.config.js
│   └── .env.example
│
├── docker-compose.yml
├── README.md
├── LICENSE
├── CONTRIBUTING.md
└── SKILL.md                        # This file
```

---

## Database Schema

### Complete PostgreSQL Schema

```sql
-- ============================================
-- USERS & CHARACTERS
-- ============================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    discord_id VARCHAR(255) UNIQUE NOT NULL,
    discord_username VARCHAR(255),
    discord_avatar VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE characters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    character_name VARCHAR(255) NOT NULL,
    world VARCHAR(100) NOT NULL,
    job VARCHAR(100),
    level INTEGER,
    is_main BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(user_id, character_name, world)
);

CREATE INDEX idx_characters_user_id ON characters(user_id);

-- ============================================
-- BOSSES & ITEMS (Seeded Data)
-- ============================================

CREATE TABLE bosses (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    difficulty VARCHAR(50),              -- Normal, Hard, Chaos, Extreme
    reset_type VARCHAR(20) NOT NULL,     -- daily, weekly, monthly
    party_size INTEGER DEFAULT 1,
    crystal_meso BIGINT,                 -- Boss crystal value
    image_url VARCHAR(500),
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    
    UNIQUE(name, difficulty)
);

CREATE TABLE items (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    category VARCHAR(100),               -- equipment, scroll, nodestone, droplet, etc.
    subcategory VARCHAR(100),            -- weapon, hat, gloves, etc.
    rarity VARCHAR(50),                  -- common, rare, epic, unique, legendary
    image_url VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE
);

-- Which items can drop from which bosses
CREATE TABLE boss_drop_table (
    id SERIAL PRIMARY KEY,
    boss_id INTEGER REFERENCES bosses(id) ON DELETE CASCADE,
    item_id INTEGER REFERENCES items(id) ON DELETE CASCADE,
    is_guaranteed BOOLEAN DEFAULT FALSE,
    
    UNIQUE(boss_id, item_id)
);

CREATE INDEX idx_boss_drop_table_boss_id ON boss_drop_table(boss_id);

-- ============================================
-- BOSS TRACKING & DROP DIARY (Core Feature)
-- ============================================

-- Each boss clear
CREATE TABLE boss_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    character_id UUID REFERENCES characters(id) ON DELETE SET NULL,
    boss_id INTEGER REFERENCES bosses(id) ON DELETE CASCADE,
    
    run_date DATE NOT NULL,
    reset_period DATE NOT NULL,          -- Which reset week/day this belongs to
    party_size INTEGER DEFAULT 1,
    cleared BOOLEAN DEFAULT TRUE,
    notes TEXT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    -- One clear per character per boss per reset period
    UNIQUE(character_id, boss_id, reset_period)
);

CREATE INDEX idx_boss_runs_user_id ON boss_runs(user_id);
CREATE INDEX idx_boss_runs_reset_period ON boss_runs(reset_period);
CREATE INDEX idx_boss_runs_boss_id ON boss_runs(boss_id);

-- Drops from each boss run (feeds community stats)
CREATE TABLE boss_run_drops (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    boss_run_id UUID REFERENCES boss_runs(id) ON DELETE CASCADE,
    item_id INTEGER REFERENCES items(id) ON DELETE CASCADE,
    quantity INTEGER DEFAULT 1,
    
    -- Optional sale tracking
    sold_for BIGINT,
    sold_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_boss_run_drops_boss_run_id ON boss_run_drops(boss_run_id);
CREATE INDEX idx_boss_run_drops_item_id ON boss_run_drops(item_id);

-- ============================================
-- TASKS & DAILIES
-- ============================================

CREATE TABLE task_templates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100),               -- dailies, weeklies, events
    reset_type VARCHAR(20) NOT NULL,     -- daily, weekly, monthly, one-time
    is_default BOOLEAN DEFAULT FALSE,    -- Show by default for new users
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE user_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    character_id UUID REFERENCES characters(id) ON DELETE SET NULL,
    
    -- Either from template or custom
    task_template_id INTEGER REFERENCES task_templates(id) ON DELETE CASCADE,
    custom_name VARCHAR(255),
    custom_reset_type VARCHAR(20),
    
    is_enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_user_tasks_user_id ON user_tasks(user_id);

CREATE TABLE task_completions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_task_id UUID REFERENCES user_tasks(id) ON DELETE CASCADE,
    reset_period DATE NOT NULL,
    completed_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(user_task_id, reset_period)
);

-- ============================================
-- COMMUNITY STATISTICS (Aggregated)
-- ============================================

CREATE TABLE drop_rate_stats (
    id SERIAL PRIMARY KEY,
    boss_id INTEGER REFERENCES bosses(id) ON DELETE CASCADE,
    item_id INTEGER REFERENCES items(id) ON DELETE CASCADE,
    
    -- All-time stats
    total_runs INTEGER DEFAULT 0,
    total_drops INTEGER DEFAULT 0,
    drop_rate DECIMAL(10, 6),
    
    -- Rolling windows
    last_7_days_runs INTEGER DEFAULT 0,
    last_7_days_drops INTEGER DEFAULT 0,
    last_7_days_rate DECIMAL(10, 6),
    
    last_30_days_runs INTEGER DEFAULT 0,
    last_30_days_drops INTEGER DEFAULT 0,
    last_30_days_rate DECIMAL(10, 6),
    
    last_calculated TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(boss_id, item_id)
);

CREATE INDEX idx_drop_rate_stats_boss_id ON drop_rate_stats(boss_id);

-- ============================================
-- USER SETTINGS
-- ============================================

CREATE TABLE user_settings (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    timezone VARCHAR(100) DEFAULT 'UTC',
    theme VARCHAR(20) DEFAULT 'dark',
    default_world VARCHAR(100),
    settings_json JSONB DEFAULT '{}',
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- HELPER FUNCTIONS
-- ============================================

CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER characters_updated_at
    BEFORE UPDATE ON characters
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
```

---

## API Endpoints

### Authentication

```
GET  /api/auth/discord
     → Redirects to Discord OAuth authorize URL

GET  /api/auth/discord/callback?code=<code>&state=<state>
     → Handles callback, creates session, redirects to frontend

POST /api/auth/logout
     → Clears session
     Response: { "message": "Logged out" }

GET  /api/auth/me
     → Returns current user
     Response: {
       "id": "uuid",
       "discord_id": "123456789",
       "discord_username": "User#1234",
       "discord_avatar": "hash"
     }
```

### Characters

```
GET    /api/characters
       → List user's characters
       Response: [{ id, character_name, world, job, level, is_main }]

POST   /api/characters
       Body: { "character_name": "string", "world": "string", "job?": "string", "level?": int }
       → Link new character

GET    /api/characters/:id
       → Get character details

PUT    /api/characters/:id
       Body: { "job?": "string", "level?": int, "is_main?": bool }
       → Update character

DELETE /api/characters/:id
       → Unlink character
```

### Bosses

```
GET  /api/bosses
     Query: ?reset_type=weekly|daily
     → List all bosses
     Response: [{ id, name, difficulty, reset_type, party_size, crystal_meso, image_url }]

GET  /api/bosses/:id
     → Boss details with drop table
     Response: {
       id, name, difficulty, ...,
       drops: [{ item_id, item_name, is_guaranteed }]
     }
```

### Boss Tracking & Drop Diary

```
GET  /api/tracking/boss-runs
     Query: ?character_id=uuid&boss_id=int&reset_period=date&limit=50&offset=0
     → List user's boss runs
     Response: [{
       id, boss_id, boss_name, character_id, run_date, reset_period,
       party_size, cleared, drops: [{ item_id, item_name, quantity, sold_for }]
     }]

POST /api/tracking/boss-runs
     Body: {
       "boss_id": int,
       "character_id": "uuid",
       "run_date?": "YYYY-MM-DD",
       "party_size?": int,
       "cleared?": bool,
       "drops?": [{ "item_id": int, "quantity?": int }]
     }
     → Log a boss clear with optional drops

PUT  /api/tracking/boss-runs/:id
     Body: { "party_size?": int, "cleared?": bool, "notes?": "string" }
     → Update boss run

DELETE /api/tracking/boss-runs/:id
       → Delete boss run (and its drops)

POST /api/tracking/boss-runs/:id/drops
     Body: { "drops": [{ "item_id": int, "quantity?": int, "sold_for?": bigint }] }
     → Add drops to existing run

DELETE /api/tracking/boss-runs/:run_id/drops/:drop_id
       → Remove a drop from run

GET  /api/tracking/weekly-summary
     Query: ?character_id=uuid
     → Current week's completion status
     Response: {
       reset_period: "YYYY-MM-DD",
       bosses: [{ boss_id, boss_name, difficulty, cleared, drops_count, meso_value }],
       total_meso: bigint
     }

GET  /api/tracking/daily-summary
     → Same structure for daily bosses
```

### Tasks

```
GET    /api/tasks
       → List user's tasks with completion status
       Response: [{ id, name, reset_type, is_enabled, completed_this_period, character_id? }]

POST   /api/tasks
       Body: {
         "task_template_id?": int,
         "custom_name?": "string",
         "custom_reset_type?": "daily|weekly",
         "character_id?": "uuid"
       }
       → Create task (from template or custom)

PUT    /api/tasks/:id
       Body: { "is_enabled?": bool, "custom_name?": "string" }

DELETE /api/tasks/:id

POST   /api/tasks/:id/complete
       → Mark task complete for current period

DELETE /api/tasks/:id/complete
       → Unmark completion for current period

GET    /api/tasks/templates
       → List available task templates
       Response: [{ id, name, description, category, reset_type }]
```

### Community Statistics (Public)

```
GET /api/stats/drop-rates
    Query: ?boss_id=int&min_sample=100
    → All drop rates meeting minimum sample
    Response: [{
      boss_id, boss_name, boss_difficulty,
      item_id, item_name,
      total_runs, total_drops, drop_rate,
      last_7_days_rate, last_30_days_rate,
      confidence: "high|medium|low",
      last_calculated
    }]

GET /api/stats/drop-rates/:boss_id
    → Drop rates for specific boss
    Response: {
      boss: { id, name, difficulty },
      total_runs: int,
      drops: [{ item_id, item_name, total_drops, drop_rate, trend }]
    }

GET /api/stats/drop-rates/:boss_id/:item_id
    → Specific item drop rate with history
    Response: {
      boss_id, item_id, current_rate, sample_size,
      history: [{ date, rate, sample_size }]
    }

GET /api/stats/boss-clears
    → How many users clear each boss weekly
    Response: [{ boss_id, boss_name, difficulty, weekly_clears, unique_users }]
```

### Calculators

```
POST /api/calculators/liberation
     Body: { "current_step": int, "coins_per_day": int }
     Response: { days_remaining, completion_date }

POST /api/calculators/symbols
     Body: {
       "symbol_type": "arcane|sacred",
       "area": "string",
       "current_level": int,
       "current_count": int,
       "daily_symbols": int
     }
     Response: { symbols_needed, days_remaining, completion_date }

POST /api/calculators/meso-income
     Body: { "character_id?": "uuid" }
     → Calculate weekly meso income from boss crystals
     Response: { weekly_meso, bosses: [{ boss_name, crystal_meso, cleared }] }
```

---

## Implementation Order

### Phase 1: Foundation (Week 1-2)
- [ ] Project setup (FastAPI + Next.js)
- [ ] PostgreSQL schema + Alembic migrations
- [ ] Discord OAuth flow
- [ ] Basic user/character CRUD
- [ ] Deploy skeleton

**Milestone:** Users can log in and add characters

### Phase 2: Boss Tracker (Week 3-4)
- [ ] Seed boss data (all GMS bosses)
- [ ] Boss tracker UI (grid/list view)
- [ ] Mark boss as cleared
- [ ] Weekly/daily reset logic
- [ ] Basic meso tracking (crystal values)

**Milestone:** Functional boss checklist

### Phase 3: Drop Diary (Week 5-6) ⭐ Core Feature
- [ ] Seed item data (boss drops)
- [ ] Drop logging UI in boss run modal
- [ ] Item search/autocomplete
- [ ] Quick-add common drops
- [ ] Personal drop history view
- [ ] Sale price tracking (optional)

**Milestone:** Users can log what dropped

### Phase 4: Community Statistics (Week 7-8) ⭐ Differentiator
- [ ] Stats aggregation background job
- [ ] Public drop rate API
- [ ] Community stats dashboard
- [ ] Trend detection (7-day vs 30-day rates)
- [ ] Data quality indicators

**Milestone:** Public drop rate statistics live

### Phase 5: Tasks & Polish (Week 9-10)
- [ ] Daily/weekly task system
- [ ] Preset tasks (Ursus, Maple Tour, etc.)
- [ ] Custom task creation
- [ ] Calculators (liberation, symbols)
- [ ] Mobile responsive
- [ ] Dark/light theme

**Milestone:** Feature complete

---

## Key Implementation Code

### Discord OAuth Service

```python
# backend/app/services/discord_oauth.py

import httpx
from urllib.parse import urlencode
import secrets

DISCORD_API_BASE = "https://discord.com/api/v10"
DISCORD_OAUTH_AUTHORIZE = "https://discord.com/api/oauth2/authorize"
DISCORD_OAUTH_TOKEN = "https://discord.com/api/oauth2/token"


class DiscordOAuthClient:
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scopes = ["identify"]
    
    def get_authorization_url(self, state: str = None) -> tuple[str, str]:
        if state is None:
            state = secrets.token_urlsafe(32)
        
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": " ".join(self.scopes),
            "state": state,
        }
        
        url = f"{DISCORD_OAUTH_AUTHORIZE}?{urlencode(params)}"
        return url, state
    
    async def exchange_code(self, code: str) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                DISCORD_OAUTH_TOKEN,
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": self.redirect_uri,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            response.raise_for_status()
            return response.json()
    
    async def get_user_info(self, access_token: str) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{DISCORD_API_BASE}/users/@me",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            response.raise_for_status()
            return response.json()
```

### Reset Time Utilities

```python
# backend/app/services/reset_times.py

from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo

# MapleStory resets at midnight UTC
RESET_TIMEZONE = ZoneInfo("UTC")


def get_daily_reset_period(dt: datetime = None) -> date:
    """Get the current daily reset period."""
    if dt is None:
        dt = datetime.now(RESET_TIMEZONE)
    return dt.date()


def get_weekly_reset_period(dt: datetime = None) -> date:
    """Get the current weekly reset period (Thursday reset)."""
    if dt is None:
        dt = datetime.now(RESET_TIMEZONE)
    
    # Find the most recent Thursday
    days_since_thursday = (dt.weekday() - 3) % 7
    reset_date = dt.date() - timedelta(days=days_since_thursday)
    return reset_date


def get_next_daily_reset() -> datetime:
    """Get the next daily reset time."""
    now = datetime.now(RESET_TIMEZONE)
    tomorrow = now.date() + timedelta(days=1)
    return datetime.combine(tomorrow, datetime.min.time(), tzinfo=RESET_TIMEZONE)


def get_next_weekly_reset() -> datetime:
    """Get the next weekly reset time (Thursday 00:00 UTC)."""
    now = datetime.now(RESET_TIMEZONE)
    days_until_thursday = (3 - now.weekday()) % 7
    if days_until_thursday == 0 and now.hour >= 0:
        days_until_thursday = 7
    next_thursday = now.date() + timedelta(days=days_until_thursday)
    return datetime.combine(next_thursday, datetime.min.time(), tzinfo=RESET_TIMEZONE)
```

### Stats Aggregation Job

```python
# backend/app/jobs/aggregate_stats.py

from sqlalchemy import select, func
from datetime import datetime, timedelta

async def aggregate_drop_rates(db):
    """
    Aggregate drop rates from boss_run_drops.
    Run as background job (hourly or daily).
    """
    now = datetime.utcnow()
    seven_days_ago = now - timedelta(days=7)
    thirty_days_ago = now - timedelta(days=30)
    
    # Get all boss/item combinations with their counts
    query = """
        SELECT 
            br.boss_id,
            brd.item_id,
            COUNT(DISTINCT br.id) as total_runs,
            COALESCE(SUM(brd.quantity), 0) as total_drops,
            COUNT(DISTINCT CASE WHEN br.created_at >= :seven_days THEN br.id END) as runs_7d,
            COALESCE(SUM(CASE WHEN br.created_at >= :seven_days THEN brd.quantity ELSE 0 END), 0) as drops_7d,
            COUNT(DISTINCT CASE WHEN br.created_at >= :thirty_days THEN br.id END) as runs_30d,
            COALESCE(SUM(CASE WHEN br.created_at >= :thirty_days THEN brd.quantity ELSE 0 END), 0) as drops_30d
        FROM boss_runs br
        LEFT JOIN boss_run_drops brd ON br.id = brd.boss_run_id
        WHERE br.cleared = true
        GROUP BY br.boss_id, brd.item_id
    """
    
    results = await db.execute(query, {
        "seven_days": seven_days_ago,
        "thirty_days": thirty_days_ago
    })
    
    for row in results:
        # Calculate rates
        drop_rate = row.total_drops / row.total_runs if row.total_runs > 0 else 0
        rate_7d = row.drops_7d / row.runs_7d if row.runs_7d > 0 else None
        rate_30d = row.drops_30d / row.runs_30d if row.runs_30d > 0 else None
        
        # Upsert into drop_rate_stats
        await db.execute("""
            INSERT INTO drop_rate_stats 
                (boss_id, item_id, total_runs, total_drops, drop_rate,
                 last_7_days_runs, last_7_days_drops, last_7_days_rate,
                 last_30_days_runs, last_30_days_drops, last_30_days_rate,
                 last_calculated)
            VALUES (:boss_id, :item_id, :total_runs, :total_drops, :drop_rate,
                    :runs_7d, :drops_7d, :rate_7d,
                    :runs_30d, :drops_30d, :rate_30d, :now)
            ON CONFLICT (boss_id, item_id) DO UPDATE SET
                total_runs = :total_runs,
                total_drops = :total_drops,
                drop_rate = :drop_rate,
                last_7_days_runs = :runs_7d,
                last_7_days_drops = :drops_7d,
                last_7_days_rate = :rate_7d,
                last_30_days_runs = :runs_30d,
                last_30_days_drops = :drops_30d,
                last_30_days_rate = :rate_30d,
                last_calculated = :now
        """, {
            "boss_id": row.boss_id,
            "item_id": row.item_id,
            "total_runs": row.total_runs,
            "total_drops": row.total_drops,
            "drop_rate": drop_rate,
            "runs_7d": row.runs_7d,
            "drops_7d": row.drops_7d,
            "rate_7d": rate_7d,
            "runs_30d": row.runs_30d,
            "drops_30d": row.drops_30d,
            "rate_30d": rate_30d,
            "now": now
        })
    
    await db.commit()
```

---

## Seed Data Structure

### bosses.json

```json
{
  "bosses": [
    {
      "name": "Zakum",
      "difficulty": "Normal",
      "reset_type": "daily",
      "party_size": 1,
      "crystal_meso": 612500,
      "sort_order": 1
    },
    {
      "name": "Zakum",
      "difficulty": "Chaos",
      "reset_type": "weekly",
      "party_size": 1,
      "crystal_meso": 16200000,
      "sort_order": 10
    },
    {
      "name": "Lucid",
      "difficulty": "Hard",
      "reset_type": "weekly",
      "party_size": 6,
      "crystal_meso": 175000000,
      "sort_order": 52
    }
  ]
}
```

### items.json

```json
{
  "items": [
    {
      "name": "Arcane Umbra Weapon Box",
      "category": "equipment",
      "subcategory": "weapon",
      "rarity": "legendary"
    },
    {
      "name": "Sealed Stone of Chaos",
      "category": "material",
      "rarity": "epic"
    },
    {
      "name": "Genesis Badge",
      "category": "equipment",
      "subcategory": "badge",
      "rarity": "legendary"
    }
  ]
}
```

### boss_drop_tables.json

```json
{
  "drop_tables": [
    {
      "boss_name": "Hard Lucid",
      "drops": [
        { "item_name": "Arcane Umbra Weapon Box", "is_guaranteed": false },
        { "item_name": "Arcane Umbra Armor Box", "is_guaranteed": false },
        { "item_name": "Diffusion Line Energy (Core)", "is_guaranteed": false },
        { "item_name": "Sealed Stone of Chaos", "is_guaranteed": false }
      ]
    }
  ]
}
```

### task_templates.json

```json
{
  "task_templates": [
    { "name": "Ursus", "category": "dailies", "reset_type": "daily", "is_default": true },
    { "name": "Maple Tour", "category": "dailies", "reset_type": "daily", "is_default": true },
    { "name": "Monster Park", "category": "dailies", "reset_type": "daily", "is_default": true },
    { "name": "Arcane River Dailies", "category": "dailies", "reset_type": "daily", "is_default": true },
    { "name": "Sacred Symbol Dailies", "category": "dailies", "reset_type": "daily", "is_default": true },
    { "name": "Weekly Arcane River", "category": "weeklies", "reset_type": "weekly", "is_default": true }
  ]
}
```

---

## Data Quality Rules

- Minimum 100 runs before showing drop rates publicly
- Flag outliers (>3 std dev from mean drops per run)
- Weight newer data higher for trend calculations
- Always show sample size + confidence level alongside rates
- Confidence: "high" (>1000 runs), "medium" (100-1000), "low" (<100)

---

## GMS Data Sources

| Data | Source |
|------|--------|
| Character name/level/world | User input (or Nexon Rankings scrape) |
| Character avatar | maplestory.io render API |
| Item/boss sprites | maplestory.io |
| Gear/equipment | Not available — not needed |

---

## Environment Variables

```env
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/maplehub

# Redis (for sessions/cache)
REDIS_URL=redis://localhost:6379

# Discord OAuth
DISCORD_CLIENT_ID=your_client_id
DISCORD_CLIENT_SECRET=your_client_secret
DISCORD_REDIRECT_URI=http://localhost:3000/api/auth/discord/callback

# App
SECRET_KEY=your-secret-key-min-32-chars
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000
```

---

## Docker Compose (Development)

```yaml
version: '3.8'
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: maplehub
      POSTGRES_USER: maplehub
      POSTGRES_PASSWORD: devpassword
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://maplehub:devpassword@db:5432/maplehub
      REDIS_URL: redis://redis:6379
    depends_on:
      - db
      - redis
    volumes:
      - ./backend:/app

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
    volumes:
      - ./frontend:/app
      - /app/node_modules

volumes:
  postgres_data:
```

---

## Drop Diary UX Flow

### Recording a Boss Run

```
1. User goes to Boss Tracker
2. Clicks "Log Run" on Hard Lucid
3. Modal appears:
   ┌─────────────────────────────────────────┐
   │  Log Hard Lucid Clear                   │
   │                                         │
   │  Character: [Dropdown - their chars]    │
   │  Date: [Today]  Party Size: [1-6]       │
   │                                         │
   │  ─── Drops ───                          │
   │  [Search items or click common drops]   │
   │                                         │
   │  Quick Add:                             │
   │  [Arcane Umbra Weapon Box] [+]          │
   │  [Diffusion Line Energy]    [+]         │
   │  [Sealed Stone of Chaos]    [+]         │
   │  [Nothing special]          [+]         │
   │                                         │
   │  Added:                                 │
   │  • Arcane Umbra Weapon Box x1  [🗑️]     │
   │                                         │
   │  [Save Run]                             │
   └─────────────────────────────────────────┘

4. Data saved → contributes to personal log AND community stats
```

---

## Resources

- **Discord OAuth:** https://discord.com/developers/docs/topics/oauth2
- **FastAPI:** https://fastapi.tiangolo.com
- **Next.js:** https://nextjs.org/docs
- **maplestory.io:** https://maplestory.io (sprites, item data)
- **MapleStory Wiki:** https://maplestory.wiki
