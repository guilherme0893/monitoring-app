from typing import List, Optional

from sqlmodel import select

from models.reading import Reading
from repositories.base import BaseRepository


class ReadingRepository(BaseRepository[Reading]):
    async def get_all(self) -> List[Reading]:
        readings = await self._session.execute(select(Reading))
        return readings.scalars().all()

    async def get_by_id(self, id: int) -> Optional[Reading]:
        reading = await self._session.get(Reading, id)
        return reading

    async def get_readings_by_well(self, well_id: int) -> List[Reading]:
        readings = await self._session.execute(select(Reading).where(Reading.well_id == well_id))
        return readings.scalars().all()
