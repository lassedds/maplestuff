"""
SQLAlchemy models for GMSTracker.

Import all models here so Alembic can detect them for autogenerate.
"""

from app.database import Base

# Import models as they are created:
# from app.models.user import User
# from app.models.character import Character
# from app.models.boss import Boss
# from app.models.item import Item
# from app.models.boss_run import BossRun
# from app.models.task import Task, UserTask, TaskCompletion
# from app.models.stats import DropRateStats

__all__ = ["Base"]
