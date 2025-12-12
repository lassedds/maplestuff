"""
Boss model for GMSTracker.
Contains all MapleStory boss definitions.
"""

from sqlalchemy import Boolean, Integer, BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Boss(Base):
    """
    MapleStory boss definition.
    Seeded from boss data, not user-created.
    """

    __tablename__ = "bosses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    difficulty: Mapped[str | None] = mapped_column(String(50))  # Normal, Hard, Chaos, Extreme
    reset_type: Mapped[str] = mapped_column(String(20), nullable=False)  # daily, weekly, monthly
    party_size: Mapped[int] = mapped_column(Integer, default=1)
    crystal_meso: Mapped[int | None] = mapped_column(BigInteger)  # Boss crystal value
    image_url: Mapped[str | None] = mapped_column(String(500))
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    drop_table: Mapped[list["BossDropTable"]] = relationship(
        "BossDropTable",
        back_populates="boss",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        if self.difficulty:
            return f"<Boss {self.difficulty} {self.name}>"
        return f"<Boss {self.name}>"

    @property
    def full_name(self) -> str:
        """Get full boss name with difficulty."""
        if self.difficulty:
            return f"{self.difficulty} {self.name}"
        return self.name


# Import here to avoid circular imports
from app.models.boss_drop_table import BossDropTable
