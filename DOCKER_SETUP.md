# Docker Setup - XP Tracker

## Quick Start

Run everything with Docker Compose:

```bash
docker-compose up --build
```

That's it! The XP tracker will be available at `http://localhost:3000/xp-tracker`

## What Gets Started

1. **PostgreSQL Database** - Stores all XP entries
2. **Redis** - Caching (if needed)
3. **Backend** - FastAPI server on port 8000
4. **Frontend** - Next.js app on port 3000

## First Time Setup

### 1. Database Migrations

Migrations run automatically on startup via `entrypoint.sh`. The XP entries table will be created automatically.

### 2. XP Table Location

The XP table CSV is mounted from `./Xp/XP_Table.csv` into the container at `/app/xp_data/XP_Table.csv`.

Make sure the file exists at:
```
./Xp/XP_Table.csv
```

If it's in a different location, update the volume mount in `docker-compose.yml`:

```yaml
volumes:
  - ./Xp:/app/xp_data:ro  # Change ./Xp to your path
```

## Accessing the Application

- **Frontend**: http://localhost:3000
- **XP Tracker**: http://localhost:3000/xp-tracker
- **API Docs**: http://localhost:8000/docs
- **Backend Health**: http://localhost:8000/health

## Stopping

```bash
docker-compose down
```

To also remove volumes (clears database):

```bash
docker-compose down -v
```

## Development Mode

The containers are set up for development with hot-reload:
- Backend code changes auto-reload
- Frontend code changes auto-reload
- Database persists in Docker volume

## Production Deployment

For production:
1. Set proper `SECRET_KEY` in environment
2. Use production database (not the dev one)
3. Build production frontend: `npm run build`
4. Use production Dockerfile (if different)
5. Set up proper CORS origins
6. Use environment variables for all secrets

## Troubleshooting

**XP table not found:**
- Check that `./Xp/XP_Table.csv` exists
- Verify the volume mount in docker-compose.yml
- Check backend logs: `docker-compose logs backend`

**Database connection issues:**
- Wait for database to be healthy (check logs)
- Migrations run automatically on startup
- Check database logs: `docker-compose logs db`

**Port already in use:**
- Change ports in docker-compose.yml if 3000 or 8000 are taken
- Update FRONTEND_URL and BACKEND_URL environment variables accordingly
