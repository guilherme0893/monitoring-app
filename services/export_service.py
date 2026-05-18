import io

from helper.export import export_as_xlsx
from services.reading_service import ReadingService


class ExportService:
    def __init__(self, reading_service: ReadingService):
        self.reading_service = reading_service

    async def export_anomalies_as_xlsx(self, well_id: int) -> io.BytesIO:
        anomalies = await self.reading_service.get_anomalies(well_id)
        return export_as_xlsx(anomalies, well_id)
