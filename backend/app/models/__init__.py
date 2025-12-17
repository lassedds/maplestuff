"""
SQLAlchemy models for GMSTracker.

Import all models here so Alembic can detect them for autogenerate.
"""

from app.database import Base
from app.models.user import User
from app.models.character import Character
from app.models.user_settings import UserSettings
from app.models.boss import Boss
from app.models.item import Item
from app.models.boss_drop_table import BossDropTable
from app.models.boss_run import BossRun, BossRunDrop
from app.models.drop_rate_stats import DropRateStats
from app.models.task import Task, UserTask, TaskCompletion
from app.models.xp_entry import XPEntry
from app.models.character_xp_snapshot import CharacterXPSnapshot

__all__ = [
    "Base",
    "User",
    "Character",
    "UserSettings",
    "Boss",
    "Item",
    "BossDropTable",
    "BossRun",
    "BossRunDrop",
    "DropRateStats",
    "Task",
    "UserTask",
    "TaskCompletion",
    "XPEntry",
    "CharacterXPSnapshot",
]
