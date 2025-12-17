# XP Tracker - Quick Start

## Run in Docker (Easiest!)

```bash
docker-compose up --build
```

That's it! 🎉

Access at: **http://localhost:3000/xp-tracker**

## What You Need

1. **Docker and Docker Compose** installed
2. **XP Table CSV** at `./Xp/XP_Table.csv` (already exists!)

## First Time

The first time you run it:
- Database migrations run automatically
- XP entries table is created
- Everything is ready to use!

## Using the Tracker

1. Go to http://localhost:3000/xp-tracker
2. Enter your daily XP:
   - Date
   - Level (200-299)
   - Old % (e.g., 0.00)
   - New % (e.g., 50.25)
3. Optionally check "Epic Dungeon" and select multiplier
4. Click "Add Entry"
5. See your 7-day average and recent entries!

## Stopping

```bash
docker-compose down
```

## Troubleshooting

**Port already in use?**
- Change ports in `docker-compose.yml` if needed

**XP table not found?**
- Make sure `./Xp/XP_Table.csv` exists
- Check `docker-compose logs backend` for errors

**Database issues?**
- Migrations run automatically on startup
- Check logs: `docker-compose logs backend`

## That's It!

No manual setup, no migrations to run manually, no configuration needed. Just `docker-compose up` and go!
