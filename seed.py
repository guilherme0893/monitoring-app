"""
Run once to seed the database with sample oil well data.
Usage: python seed.py
"""
import asyncio
import random
from datetime import datetime, timedelta

from sqlmodel import select

from config.database import AsyncSessionLocal, init_db
from models.reading import Reading
from models.well import Well
from models.well_type import WellType, WellTypeEnum

SAMPLE_WELL_TYPES = [
    WellType(type=WellTypeEnum.producer),
    WellType(type=WellTypeEnum.injector),
]

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
        type_id=1,
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
        type_id=1,
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
        type_id=2,
    ),
]


async def seed() -> None:
    await init_db()

    async with AsyncSessionLocal() as session:
        # Skip if already seeded
        result = await session.execute(select(Well))
        existing_wells = result.scalars().all()
        if existing_wells:
            print("Database already has wells — skipping well seed.")
            wells = existing_wells
        else:
            session.add_all(SAMPLE_WELL_TYPES)
            session.add_all(SAMPLE_WELLS)
            await session.commit()
            print(f"Seeded {len(SAMPLE_WELL_TYPES)} well types.")
            print(f"Seeded {len(SAMPLE_WELLS)} wells.")
            wells = SAMPLE_WELLS

        # Seed readings if missing
        result = await session.execute(select(Reading))
        if result.scalars().first():
            print("Database already has readings — skipping readings seed.")
            return

        readings = generate_readings(wells, days=60, interval_hours=2)
        session.add_all(readings)
        await session.commit()
        print(f"Seeded {len(readings)} readings across {len(wells)} wells.")


def generate_readings(wells, days: int = 60, interval_hours: int = 2) -> list[Reading]:
    """Generate random readings for each well covering `days` days, every `interval_hours`."""
    rng = random.Random(42)
    readings: list[Reading] = []
    end = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
    start = end - timedelta(days=days)
    steps = (days * 24) // interval_hours

    for well in wells:
        # Baselines per well to make the data feel coherent
        base_pressure = rng.uniform(1800.0, 3500.0)
        base_temp = rng.uniform(60.0, 110.0)
        base_oil = rng.uniform(200.0, 1500.0)
        base_gas = rng.uniform(500.0, 4000.0)
        base_water = rng.uniform(50.0, 800.0)

        for i in range(steps):
            ts = start + timedelta(hours=i * interval_hours)
            readings.append(
                Reading(
                    well_id=well.id,
                    timestamp=ts,
                    pressure_psi=round(base_pressure + rng.uniform(-150.0, 150.0), 2),
                    temperature_c=round(base_temp + rng.uniform(-5.0, 5.0), 2),
                    oil_bpd=round(max(0.0, base_oil + rng.uniform(-100.0, 100.0)), 2),
                    gas_mscfd=round(max(0.0, base_gas + rng.uniform(-300.0, 300.0)), 2),
                    water_bpd=round(max(0.0, base_water + rng.uniform(-50.0, 50.0)), 2),
                    created_at=ts,
                )
            )
    return readings


if __name__ == "__main__":
    asyncio.run(seed())
