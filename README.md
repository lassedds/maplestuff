# MapleHub OSS

Open-source MapleStory companion app with boss tracking, drop diary, daily/weekly tasks, and crowdsourced community drop rate statistics.

## Features

- **Boss Tracker** - Track your weekly and daily boss clears
- **Drop Diary** - Log your drops and contribute to community statistics
- **Character Management** - Manage multiple characters across different worlds
- **Community Statistics** - View aggregated drop rates from all users
- **XP Tracker** - Track daily XP gains with automatic calculations and 7-day averages

## Tech Stack

- **Backend**: FastAPI (Python 3.11+)
- **Frontend**: Next.js 14+ (React, TypeScript)
- **Database**: PostgreSQL
- **Cache**: Redis
- **Auth**: Discord OAuth2

## Quick Start

### Option 1: Docker (Recommended - Easiest)

```bash
# Make sure XP table exists at ./Xp/XP_Table.csv
docker-compose up --build
```

Access the app at:
- Frontend: http://localhost:3000
- XP Tracker: http://localhost:3000/xp-tracker
- API Docs: http://localhost:8000/docs

See [DOCKER_SETUP.md](./DOCKER_SETUP.md) for details.

### Option 2: Local Development

### Prerequisites

- Docker and Docker Compose (for database/redis)
- Node.js 18+ and npm
- Python 3.11+
- Discord OAuth application (see [SETUP_GUIDE.md](./SETUP_GUIDE.md))

### 1. Start Database and Redis

```bash
docker-compose up -d db redis
```

### 2. Set Up Backend

```bash
cd backend

# Create .env file (copy from .env.example and fill in values)
cp .env.example .env
# Edit .env with your Discord OAuth credentials

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start backend server
uvicorn app.main:app --reload
```

The backend will be available at `http://localhost:8000`

### 3. Set Up Frontend

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local file
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Environment Variables

### Backend (.env)

See `backend/.env.example` for all required variables. Key ones:

- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `DISCORD_CLIENT_ID` - Discord OAuth client ID
- `DISCORD_CLIENT_SECRET` - Discord OAuth client secret
- `DISCORD_REDIRECT_URI` - Must be `http://localhost:8000/api/auth/discord/callback`
- `SECRET_KEY` - Random 32+ character string for session security

### Frontend (.env.local)

- `NEXT_PUBLIC_API_URL` - Backend API URL (default: `http://localhost:8000`)

## Development

### Backend

- API docs available at `http://localhost:8000/docs`
- Uses FastAPI with async SQLAlchemy
- Sessions stored in Redis

### Frontend

- Uses Next.js App Router
- TypeScript for type safety
- Tailwind CSS for styling

## Project Structure

```
├── backend/          # FastAPI backend
│   ├── app/
│   │   ├── models/   # SQLAlchemy models
│   │   ├── routers/  # API endpoints
│   │   ├── schemas/  # Pydantic schemas
│   │   └── services/ # Business logic
│   └── alembic/      # Database migrations
├── frontend/         # Next.js frontend
│   └── src/
│       ├── app/      # Next.js pages
│       ├── components/
│       └── services/ # API client
└── docker-compose.yml
```

## Documentation

- [SKILL.md](./SKILL.md) - Detailed development guide and project vision
- [SETUP_GUIDE.md](./SETUP_GUIDE.md) - Setup instructions for external services

## License

MIT

