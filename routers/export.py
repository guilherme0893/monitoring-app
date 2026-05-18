from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import get_session
from repositories.reading_repository import ReadingRepository
from repositories.well_repository import WellRepository
from services.export_service import ExportService
from services.reading_service import ReadingService
from services.well_service import WellService


export = APIRouter(
    prefix="/xlsx",
    tags=["xlsx"]
)


def get_export_service(session: AsyncSession = Depends(get_session)) -> ExportService:
    return ExportService(ReadingService(ReadingRepository(session)))


def get_well_service(session: AsyncSession = Depends(get_session)) -> WellService:
    return WellService(WellRepository(session))


@export.get("/anomalies/{well_id}")
async def export_anomalies(
    well_id: int,
    service: ExportService = Depends(get_export_service),
    well_service: WellService = Depends(get_well_service),
):
    if not await well_service.get_by_id(well_id):
        raise HTTPException(status_code=404, detail="Well not found")

    anomalies = await service.export_anomalies_as_xlsx(well_id)

    if not anomalies.getbuffer().nbytes:
        return Response(
            status_code=204,
            headers={"X-Detail": "No anomalies found for this well"},
        )

    filename = f"anomalies_well_{well_id}.xlsx"
    headers = {"Content-Disposition": f"attachment; filename={filename}"}
    return StreamingResponse(
        anomalies,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )
