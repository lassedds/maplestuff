"""
Seed script to load initial data into the database.
Run with: python -m seeds.seed_db
"""

import asyncio
import json
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_maker, engine, Base
from app.models import Boss, Item, BossDropTable


SEEDS_DIR = Path(__file__).parent


async def load_bosses(session: AsyncSession) -> dict[str, int]:
    """Load bosses from JSON and return name+difficulty -> id mapping."""
    with open(SEEDS_DIR / "bosses.json") as f:
        data = json.load(f)

    boss_map = {}
    for boss_data in data["bosses"]:
        # Check if boss already exists
        result = await session.execute(
            select(Boss).where(
                Boss.name == boss_data["name"],
                Boss.difficulty == boss_data.get("difficulty"),
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            boss_map[f"{boss_data['name']}|{boss_data.get('difficulty')}"] = existing.id
            continue

        boss = Boss(
            name=boss_data["name"],
            difficulty=boss_data.get("difficulty"),
            reset_type=boss_data["reset_type"],
            party_size=boss_data.get("party_size", 1),
            crystal_meso=boss_data.get("crystal_meso"),
            image_url=boss_data.get("image_url"),
            sort_order=boss_data.get("sort_order", 0),
            is_active=True,
        )
        session.add(boss)
        await session.flush()
        boss_map[f"{boss_data['name']}|{boss_data.get('difficulty')}"] = boss.id

    await session.commit()
    print(f"Loaded {len(boss_map)} bosses")
    return boss_map


async def load_items(session: AsyncSession) -> dict[str, int]:
    """Load items from JSON and return name -> id mapping."""
    with open(SEEDS_DIR / "items.json") as f:
        data = json.load(f)

    item_map = {}
    for item_data in data["items"]:
        # Check if item already exists
        result = await session.execute(
            select(Item).where(Item.name == item_data["name"])
        )
        existing = result.scalar_one_or_none()

        if existing:
            item_map[item_data["name"]] = existing.id
            continue

        item = Item(
            name=item_data["name"],
            category=item_data.get("category"),
            subcategory=item_data.get("subcategory"),
            rarity=item_data.get("rarity"),
            image_url=item_data.get("image_url"),
            is_active=True,
        )
        session.add(item)
        await session.flush()
        item_map[item_data["name"]] = item.id

    await session.commit()
    print(f"Loaded {len(item_map)} items")
    return item_map


async def load_drop_tables(
    session: AsyncSession,
    boss_map: dict[str, int],
    item_map: dict[str, int],
) -> int:
    """Load boss drop tables from JSON."""
    with open(SEEDS_DIR / "boss_drop_tables.json") as f:
        data = json.load(f)

    count = 0
    for entry in data["drop_tables"]:
        boss_key = f"{entry['boss']['name']}|{entry['boss'].get('difficulty')}"
        boss_id = boss_map.get(boss_key)

        if not boss_id:
            print(f"Warning: Boss not found: {boss_key}")
            continue

        for drop in entry["drops"]:
            item_id = item_map.get(drop["item"])

            if not item_id:
                print(f"Warning: Item not found: {drop['item']}")
                continue

            # Check if drop table entry already exists
            result = await session.execute(
                select(BossDropTable).where(
                    BossDropTable.boss_id == boss_id,
                    BossDropTable.item_id == item_id,
                )
            )
            existing = result.scalar_one_or_none()

            if existing:
                continue

            drop_entry = BossDropTable(
                boss_id=boss_id,
                item_id=item_id,
                is_guaranteed=drop.get("is_guaranteed", False),
            )
            session.add(drop_entry)
            count += 1

    await session.commit()
    print(f"Loaded {count} drop table entries")
    return count


async def seed_database():
    """Run all seed operations."""
    print("Starting database seed...")

    async with async_session_maker() as session:
        # Load in order due to foreign key dependencies
        boss_map = await load_bosses(session)
        item_map = await load_items(session)
        await load_drop_tables(session, boss_map, item_map)

    print("Database seed complete!")


async def reset_and_seed():
    """Drop all tables, recreate, and seed."""
    print("Resetting database...")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    await seed_database()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--reset":
        asyncio.run(reset_and_seed())
    else:
        asyncio.run(seed_database())
