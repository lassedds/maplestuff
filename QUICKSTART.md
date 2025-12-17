# Quick Start Guide

Get MapleHub OSS running in 5 minutes!

## Step 1: Start Database & Redis

```bash
docker-compose up -d db redis
```

Wait a few seconds for services to start.

## Step 2: Set Up Backend

```bash
cd backend

# Create .env file (NO LOGIN MODE - see NO_LOGIN_MODE.md for details)
cat > .env << EOF
DATABASE_URL=postgresql://maplehub:devpassword@localhost:5432/maplehub
REDIS_URL=redis://localhost:6379
SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
DEBUG=true
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000
EOF

# Note: Discord OAuth credentials are NOT required in DEBUG mode
# The app will use a mock user automatically

# Install Python dependencies (use venv recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start backend server
uvicorn app.main:app --reload
```

Backend will run on `http://localhost:8000`

## Step 3: Set Up Frontend

In a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Start frontend
npm run dev
```

Frontend will run on `http://localhost:3000`

## Step 4: Test It!

1. Open `http://localhost:3000`
2. You'll be automatically redirected to the dashboard (no login required!)
3. Try adding a character on the Characters page

**Note:** The app is currently in **no-login mode** (DEBUG=true). See [NO_LOGIN_MODE.md](./NO_LOGIN_MODE.md) for details.

### Optional: Enable Discord OAuth Login

If you want to enable real Discord OAuth login:

1. Go to https://discord.com/developers/applications
2. Create a new application
3. Go to OAuth2 → General
4. Copy Client ID and Client Secret
5. Add redirect URI: `http://localhost:8000/api/auth/discord/callback`
6. Update your `backend/.env`:
   ```env
   DEBUG=false
   DISCORD_CLIENT_ID=your_client_id
   DISCORD_CLIENT_SECRET=your_client_secret
   DISCORD_REDIRECT_URI=http://localhost:8000/api/auth/discord/callback
   ```

## Troubleshooting

### Database connection error
- Make sure Docker containers are running: `docker-compose ps`
- Check DATABASE_URL in backend/.env

### Redis connection error
- Make sure Redis container is running
- Check REDIS_URL in backend/.env

### Discord OAuth not working
- Verify redirect URI matches exactly in Discord Developer Portal
- Check DISCORD_CLIENT_ID and DISCORD_CLIENT_SECRET in backend/.env
- Make sure redirect URI is `http://localhost:8000/api/auth/discord/callback` (backend, not frontend!)

### Frontend can't connect to backend
- Check NEXT_PUBLIC_API_URL in frontend/.env.local
- Make sure backend is running on port 8000
- Check browser console for CORS errors

## Next Steps

- Add your first character on the Characters page
- Check out the API docs at `http://localhost:8000/docs`
- Read [SKILL.md](./SKILL.md) for development details

