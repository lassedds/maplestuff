"""
API routers for GMSTracker.
"""

from app.routers.auth import router as auth_router
from app.routers.bosses import router as bosses_router
from app.routers.characters import router as characters_router
from app.routers.items import router as items_router
from app.routers.tracking import router as tracking_router
from app.routers.stats import router as stats_router

__all__ = ["auth_router", "bosses_router", "characters_router", "items_router", "tracking_router", "stats_router"]
