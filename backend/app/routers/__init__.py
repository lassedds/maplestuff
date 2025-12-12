"""
API routers for GMSTracker.
"""

from app.routers.auth import router as auth_router
from app.routers.characters import router as characters_router

__all__ = ["auth_router", "characters_router"]
