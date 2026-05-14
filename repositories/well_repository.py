from typing import Optional

from sqlmodel import select

from models.well import Well
from repositories.base import BaseRepository


class WellRepository(BaseRepository[Well]):
    async def get_all(self) -> list[Well]:
        wells = await self._session.execute(select(Well))
        return wells.scalars().all()

    async def get_by_id(self, id: int) -> Optional[Well]:
        well = await self._session.get(Well, id)
        return well