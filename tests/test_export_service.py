import io
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import openpyxl

from schemas.reading import ReadingResponse
from services.export_service import ExportService
from services.reading_service import ReadingService


def _make_service(reading_service: ReadingService) -> ExportService:
    return ExportService(reading_service)


def _make_response(**kwargs) -> ReadingResponse:
    defaults = dict(
        id=1,
        well_id=1,
        timestamp=datetime(2024, 1, 1, tzinfo=timezone.utc),
        pressure_psi=3000.0,
        temperature_c=150.0,
        oil_bpd=500.0,
        gas_mscfd=2000.0,
        water_bpd=100.0,
        created_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
    )
    return ReadingResponse(**{**defaults, **kwargs})


class TestExportAnomaliesAsXLSX:
    async def test_returns_xlsx_with_anomalies(self):
        anomalies = [
            _make_response(id=1, timestamp=datetime(2024, 1, 1, tzinfo=timezone.utc)),
            _make_response(
                id=2, 
                timestamp=datetime(2024, 1, 2, tzinfo=timezone.utc), 
                pressure_psi=3200.0, 
                temperature_c=160.0, 
                oil_bpd=600.0, 
                gas_mscfd=2500.0, 
                water_bpd=150.0
            ),
        ]
        reading_service = MagicMock(spec=ReadingService)
        reading_service.get_anomalies = AsyncMock(return_value=anomalies)
        service = _make_service(reading_service)

        result = await service.export_anomalies_as_xlsx(1)

        reading_service.get_anomalies.assert_awaited_once_with(1)
        assert isinstance(result, io.BytesIO)
        assert result.getbuffer().nbytes > 0

        wb = openpyxl.load_workbook(result)
        ws = wb.active
        assert ws.title == "Anomalies - Well 1"
        rows = list(ws.iter_rows(values_only=True))
        assert rows[0] == (
            "id", 
            "well_id", 
            "timestamp", 
            "pressure_psi", 
            "temperature_c", 
            "oil_bpd", 
            "gas_mscfd", 
            "water_bpd", 
            "created_at"
        )
        assert len(rows) == 3

    async def test_returns_empty_xlsx_when_no_anomalies(self):
        reading_service = MagicMock(spec=ReadingService)
        reading_service.get_anomalies = AsyncMock(return_value=[])
        service = _make_service(reading_service)

        result = await service.export_anomalies_as_xlsx(1)

        reading_service.get_anomalies.assert_awaited_once_with(1)
        assert isinstance(result, io.BytesIO)
        assert result.getbuffer().nbytes == 0
