"""
MapleHub OSS - FastAPI Backend
Main application entry point
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import (
    auth_router,
    bosses_router,
    characters_router,
    items_router,
    tracking_router,
    stats_router,
    tasks_router,
    maplestory_router,
    diary_router,
    xp_router,
)
from app.routers.character_xp import router as character_xp_router
from app.redis import init_redis, close_redis, redis_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup/shutdown."""
    # Startup
    try:
        await init_redis()
        print("Redis connected")
    except Exception as e:
        print(f"Redis connection failed (will retry on use): {e}")

    yield

    # Shutdown
    await close_redis()
    print("Redis disconnected")


app = FastAPI(
    title="MapleHub OSS API",
    description="Open-source MapleStory companion with boss tracking and community drop statistics",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router, prefix="/api")
app.include_router(bosses_router, prefix="/api")
app.include_router(characters_router, prefix="/api")
app.include_router(items_router, prefix="/api")
app.include_router(tracking_router, prefix="/api")
app.include_router(stats_router, prefix="/api")
app.include_router(tasks_router, prefix="/api")
app.include_router(maplestory_router, prefix="/api")
app.include_router(diary_router, prefix="/api")
app.include_router(xp_router)
app.include_router(character_xp_router)


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    redis_status = "connected" if redis_client else "disconnected"
    return {
        "status": "healthy",
        "version": "0.1.0",
        "redis": redis_status,
    }


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": "MapleHub OSS API",
        "version": "0.1.0",
        "docs": "/docs",
    }
