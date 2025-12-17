# XP Tracker Website - Setup Guide

## ✅ What's Been Created

A complete web-based XP tracker that replaces the Google Sheets solution with a proper backend/frontend application.

## Backend Components

### 1. Database Model (`backend/app/models/xp_entry.py`)
- Stores daily XP entries with all calculated values
- Links to user accounts
- Tracks Epic Dungeon XP and multipliers

### 2. API Router (`backend/app/routers/xp.py`)
- `POST /api/xp` - Create new XP entry
- `GET /api/xp` - List entries (with date filtering)
- `GET /api/xp/stats` - Get 7-day average and statistics
- `GET /api/xp/{id}` - Get specific entry
- `PUT /api/xp/{id}` - Update entry
- `DELETE /api/xp/{id}` - Delete entry

### 3. Services
- `backend/app/services/xp_table.py` - Loads XP table from CSV, calculates XP gained
- `backend/app/services/epic_dungeon.py` - Provides Epic Dungeon XP values per level

### 4. Schemas (`backend/app/schemas/xp_entry.py`)
- Request/response models for API

## Frontend Components

### 1. Page (`frontend/src/app/xp-tracker/page.tsx`)
- Daily entry form
- 7-day average display
- Recent entries table
- Epic Dungeon toggle and multiplier selection

### 2. Types (`frontend/src/types/index.ts`)
- TypeScript interfaces for XP tracking

### 3. API Client (`frontend/src/services/api.ts`)
- Methods to interact with XP endpoints

## Setup Instructions

### Option 1: Docker (Easiest)

```bash
# Make sure XP table exists at ./Xp/XP_Table.csv
docker-compose up --build
```

Access at: `http://localhost:3000/xp-tracker`

See [DOCKER_SETUP.md](./DOCKER_SETUP.md) for details.

### Option 2: Local Development

### 1. Create Database Migration

```bash
cd backend
alembic revision --autogenerate -m "create_xp_entries_table"
alembic upgrade head
```

### 2. Verify XP Table Path

The XP table service looks for the CSV at:
```
./Xp/XP_Table.csv  (relative to project root)
```

In Docker, it's mounted at `/app/xp_data/XP_Table.csv`.

If your path is different, update `backend/app/services/xp_table.py`.

### 3. Start Backend

```bash
cd backend
uvicorn app.main:app --reload
```

### 4. Start Frontend

```bash
cd frontend
npm run dev
```

### 5. Access the Tracker

Navigate to: `http://localhost:3000/xp-tracker`

## Features

✅ **Automatic Calculations**
- XP gained calculated from level and % difference
- Epic Dungeon XP looked up from table
- Total daily XP automatically computed

✅ **7-Day Average**
- Automatically calculates average XP over last 7 days
- Includes Epic Dungeon XP in calculations

✅ **Epic Dungeon Support**
- Checkbox to mark Epic Dungeon completion
- Multiplier selection (1x, 4x bonus, 8x bonus)
- XP automatically added to daily total

✅ **Data Persistence**
- All entries stored in database
- Linked to user accounts
- Can edit/delete entries

✅ **Uses Exact NEW AGE Values**
- XP table loaded from CSV with exact values
- Epic Dungeon XP from lookup table

## Usage

1. **Add Daily Entry:**
   - Enter date, level, old %, new %
   - Optionally check Epic Dungeon and select multiplier
   - Click "Add Entry"

2. **View Statistics:**
   - 7-day average displayed at top
   - Recent entries shown in table below

3. **Edit/Delete:**
   - (Can be added later with edit buttons in table)

## Epic Dungeon Multipliers

- **1** = Base rewards (1x)
- **4** = 4x bonus (5x total: base + 4x bonus)
- **8** = 8x bonus (9x total: base + 8x bonus)

## Notes

- XP table must be at the specified path
- Epic Dungeon XP values are hardcoded in `epic_dungeon.py` - update if needed
- All calculations happen server-side for accuracy
- Data is user-specific (requires authentication)

## Next Steps (Optional Enhancements)

- Add edit/delete buttons to entries table
- Add date range filtering
- Add charts/graphs for XP trends
- Export to CSV functionality
- Multiple character support
- Weekly Epic Dungeon validation
