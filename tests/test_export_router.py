import io
from datetime import datetime

import openpyxl
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from models.reading import Reading
from models.well import Well
from tests.test_wells_router import WELL_PAYLOAD

# temperature_c=150 exceeds the 120 °C threshold → always flagged as anomalous
ANOMALOUS_READING_PAYLOAD = {
    "timestamp": datetime(2024, 1, 1, 0, 0, 0),
    "pressure_psi": 3000.0,
    "temperature_c": 150.0,
    "oil_bpd": 500.0,
    "gas_mscfd": 2000.0,
    "water_bpd": 100.0,
}

# All values below every threshold → never flagged as anomalous
NORMAL_READING_PAYLOAD = {
    "timestamp": datetime(2024, 1, 1, 0, 0, 0),
    "pressure_psi": 100.0,
    "temperature_c": 50.0,
    "oil_bpd": 10.0,
    "gas_mscfd": 100.0,
    "water_bpd": 10.0,
}


async def _seed_well(session: AsyncSession) -> Well:
    well = Well(**WELL_PAYLOAD)
    session.add(well)
    await session.commit()
    await session.refresh(well)
    return well


async def _seed_anomalous_reading(session: AsyncSession) -> Reading:
    well = await _seed_well(session)
    reading = Reading(**ANOMALOUS_READING_PAYLOAD, well_id=well.id)
    session.add(reading)
    await session.commit()
    await session.refresh(reading)
    return reading


async def _seed_normal_reading(session: AsyncSession) -> Reading:
    well = await _seed_well(session)
    reading = Reading(**NORMAL_READING_PAYLOAD, well_id=well.id)
    session.add(reading)
    await session.commit()
    await session.refresh(reading)
    return reading


# ---------------------------------------------------------------------------
# GET /xlsx/anomalies/{well_id}
# ---------------------------------------------------------------------------

class TestGetExportAnomalies:
    async def test_returns_xlsx_with_anomalies(self, client: AsyncClient, session: AsyncSession):
        reading = await _seed_anomalous_reading(session)

        response = await client.get(f"/xlsx/anomalies/{reading.well_id}")

        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        assert response.headers["Content-Disposition"] == f"attachment; filename=anomalies_well_{reading.well_id}.xlsx"

        wb = openpyxl.load_workbook(io.BytesIO(response.content))
        ws = wb.active
        assert ws.title == f"Anomalies - Well {reading.well_id}"
        rows = list(ws.iter_rows(values_only=True))
        assert rows[0] == ("id", "well_id", "timestamp", "pressure_psi", "temperature_c", "oil_bpd", "gas_mscfd", "water_bpd", "created_at")
        assert len(rows) == 2  # header + 1 data row

    async def test_returns_204_when_no_readings(self, client: AsyncClient, session: AsyncSession):
        """Well exists but has no readings at all → no anomalies → 204 with detail header."""
        well = await _seed_well(session)

        response = await client.get(f"/xlsx/anomalies/{well.id}")

        assert response.status_code == 204
        assert response.headers["x-detail"] == "No anomalies found for this well"
        assert not response.content

    async def test_returns_204_when_readings_are_not_anomalous(self, client: AsyncClient, session: AsyncSession):
        """Well has readings but none exceed any threshold → no anomalies → 204 with detail header."""
        reading = await _seed_normal_reading(session)

        response = await client.get(f"/xlsx/anomalies/{reading.well_id}")

        assert response.status_code == 204
        assert response.headers["x-detail"] == "No anomalies found for this well"
        assert not response.content

    async def test_returns_404_when_well_does_not_exist(self, client: AsyncClient, session: AsyncSession):
        """well_id does not exist in the database → 404."""
        response = await client.get("/xlsx/anomalies/99999")

        assert response.status_code == 404
        assert "application/json" in response.headers["Content-Type"]
        assert response.json()["detail"] == "Well not found"
