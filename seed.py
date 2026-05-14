"""
Run once to seed the database with sample oil well data.
Usage: python seed.py
"""
import asyncio
from datetime import datetime

from sqlmodel import select

from config.database import AsyncSessionLocal, init_db
from models.well import Well

SAMPLE_WELLS = [
    Well(
        name="Well A-01",
        field_name="Campos Basin",
        latitude=-22.5,
        longitude=-40.2,
        depth_m=3500.0,
        status="active",
        operator="Petrobras",
        spud_date=datetime(2020, 3, 15),
    ),
    Well(
        name="Well B-07",
        field_name="Santos Basin",
        latitude=-24.1,
        longitude=-42.8,
        depth_m=5200.0,
        status="active",
        operator="Shell",
        spud_date=datetime(2018, 7, 22),
    ),
    Well(
        name="Well C-03",
        field_name="Campos Basin",
        latitude=-22.9,
        longitude=-40.7,
        depth_m=2800.0,
        status="inactive",
        operator="Petrobras",
        spud_date=datetime(2015, 11, 5),
    ),
]


async def seed() -> None:
    await init_db()

    async with AsyncSessionLocal() as session:
        # Skip if already seeded
        result = await session.execute(select(Well))
        if result.scalars().first():
            print("Database already has wells — skipping seed.")
            return

        session.add_all(SAMPLE_WELLS)
        await session.commit()
        print(f"Seeded {len(SAMPLE_WELLS)} wells.")


if __name__ == "__main__":
    asyncio.run(seed())
