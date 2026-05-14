from typing import Optional

from helper.anomaly import check_anomalies
from models.reading import Reading
from repositories.reading_repository import ReadingRepository
from schemas.reading import ReadingResponse
from services.base import BaseService


class ReadingService(BaseService[Reading]):
    def __init__(self, repository: ReadingRepository) -> None:
        self._repository = repository

    async def get_all(self) -> list[Reading]:
        return await self._repository.get_all()

    async def get_by_id(self, id: int) -> Optional[Reading]:
        return await self._repository.get_by_id(id)

    async def get_readings_by_well(self, well_id: int) -> list[Reading]:
        return await self._repository.get_readings_by_well(well_id)

    async def get_anomalies(self, well_id: int) -> list[ReadingResponse]:
        readings = await self._repository.get_readings_by_well(well_id)
        return check_anomalies(readings)
