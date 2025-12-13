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

# Create .env file
cat > .env << EOF
DATABASE_URL=postgresql://maplehub:devpassword@localhost:5432/maplehub
REDIS_URL=redis://localhost:6379
DISCORD_CLIENT_ID=your_discord_client_id_here
DISCORD_CLIENT_SECRET=your_discord_client_secret_here
DISCORD_REDIRECT_URI=http://localhost:8000/api/auth/discord/callback
SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
DEBUG=true
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000
EOF

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

## Step 4: Get Discord OAuth Credentials

1. Go to https://discord.com/developers/applications
2. Create a new application
3. Go to OAuth2 → General
4. Copy Client ID and Client Secret
5. Add redirect URI: `http://localhost:8000/api/auth/discord/callback`
6. Update your `backend/.env` with these values

## Step 5: Test It!

1. Open `http://localhost:3000`
2. Click "Login with Discord"
3. Authorize the app
4. You should be redirected back and logged in!

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

