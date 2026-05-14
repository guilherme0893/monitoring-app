from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import get_session
from repositories.well_repository import WellRepository
from schemas.well import WellResponse
from services.well_service import WellService

wells = APIRouter(
    prefix="/wells",
    tags=["wells"],
)


def get_well_service(session: AsyncSession = Depends(get_session)) -> WellService:
    return WellService(WellRepository(session))


@wells.get("/", response_model=list[WellResponse])
async def get_wells(service: WellService = Depends(get_well_service)):
    return await service.get_all()


@wells.get("/{well_id}", response_model=WellResponse)
async def get_well_by_id(well_id: int, service: WellService = Depends(get_well_service)):
    well = await service.get_by_id(well_id)
    if not well:
        raise HTTPException(status_code=404, detail="Well not found")
    return well

