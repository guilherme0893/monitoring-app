from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import get_session
from repositories.reading_repository import ReadingRepository
from schemas.reading import ReadingResponse
from services.reading_service import ReadingService


readings = APIRouter(
    prefix="/readings",
    tags=["readings"]
)

def get_reading_service(session: AsyncSession = Depends(get_session)) -> ReadingService:
    return ReadingService(ReadingRepository(session))


@readings.get("/", response_model=list[ReadingResponse])
async def get_readings(service: ReadingService = Depends(get_reading_service)):
    return await service.get_all()


@readings.get("/{reading_id}", response_model=ReadingResponse)
async def get_reading_by_id(reading_id: int, service: ReadingService = Depends(get_reading_service)):
    reading = await service.get_by_id(reading_id)
    if not reading:
        raise HTTPException(status_code=404, detail="Reading not found")
    return reading


@readings.get("/well/{well_id}", response_model=list[ReadingResponse])
async def get_readings_by_well(well_id: int, service: ReadingService = Depends(get_reading_service)):
    readings = await service.get_readings_by_well(well_id)
    if not readings:
        raise HTTPException(status_code=404, detail="No readings found for this well")
    return readings
