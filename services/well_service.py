from typing import Optional

from models.well import Well
from repositories.well_repository import WellRepository
from services.base import BaseService


class WellService(BaseService[Well]):
    def __init__(self, repository: WellRepository) -> None:
        self._repository = repository

    async def get_all(self) -> list[Well]:
        return await self._repository.get_all()

    async def get_by_id(self, id: int) -> Optional[Well]:
        return await self._repository.get_by_id(id)
