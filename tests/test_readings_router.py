from datetime import datetime
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from models.reading import Reading
from models.well import Well
from tests.test_wells_router import WELL_PAYLOAD

READING_PAYLOAD = {
    "timestamp": datetime(2024, 1, 1, 0, 0, 0),
    "pressure_psi": 3000.0,
    "temperature_c": 150.0,
    "oil_bpd": 500.0,
    "gas_mscfd": 2000.0,
    "water_bpd": 100.0,
}


async def _seed_well(session: AsyncSession) -> Well:
    well = Well(**WELL_PAYLOAD)
    session.add(well)
    await session.commit()
    await session.refresh(well)
    return well


async def _seed_reading(session: AsyncSession) -> Reading:
    well = await _seed_well(session)
    reading = Reading(**READING_PAYLOAD, well_id=well.id)
    session.add(reading)
    await session.commit()
    await session.refresh(reading)
    return reading


# ---------------------------------------------------------------------------
# GET /readings/
# ---------------------------------------------------------------------------

class TestGetReadings:
    async def test_returns_empty_list_when_no_readings(self, client: AsyncClient, session: AsyncSession):
        response = await client.get("/readings/")
        assert response.status_code == 200
        assert response.json() == []

    async def test_returns_list_with_seeded_reading(self, client: AsyncClient, session: AsyncSession):
        await _seed_well(session)
        await _seed_reading(session)
        response = await client.get("/readings/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["pressure_psi"] == READING_PAYLOAD["pressure_psi"]
        assert data[0]["temperature_c"] == READING_PAYLOAD["temperature_c"]
        assert data[0]["oil_bpd"] == READING_PAYLOAD["oil_bpd"]
        assert data[0]["gas_mscfd"] == READING_PAYLOAD["gas_mscfd"]
        assert data[0]["water_bpd"] == READING_PAYLOAD["water_bpd"]


# ---------------------------------------------------------------------------
# GET /read


class TestGetReadingById:
    async def test_returns_reading_when_found(self, client: AsyncClient, session: AsyncSession):
        await _seed_well(session)
        reading = await _seed_reading(session)
        response = await client.get(f"/readings/{reading.id}")
        assert response.status_code == 200
        body = response.json()
        assert body["id"] == reading.id
        assert body["timestamp"] == READING_PAYLOAD["timestamp"].isoformat()
        assert body["pressure_psi"] == READING_PAYLOAD["pressure_psi"]
        assert body["temperature_c"] == READING_PAYLOAD["temperature_c"]
        assert body["oil_bpd"] == READING_PAYLOAD["oil_bpd"]
        assert body["gas_mscfd"] == READING_PAYLOAD["gas_mscfd"]
        assert body["water_bpd"] == READING_PAYLOAD["water_bpd"]

    async def test_returns_404_when_not_found(self, client: AsyncClient):
        response = await client.get("/readings/999999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Reading not found"

    async def test_response_schema_has_required_fields(self, client: AsyncClient, session: AsyncSession):
        reading = await _seed_reading(session)
        response = await client.get(f"/readings/{reading.id}")
        body = response.json()
        for field in (
            "id",
            "timestamp",
            "pressure_psi",
            "temperature_c",
            "oil_bpd",
            "gas_mscfd",
            "water_bpd",
            "well_id",
        ):
            assert field in body, f"Missing field: {field}"

# ---------------------------------------------------------------------------
# GET /readings/well/{well_id}
# ---------------------------------------------------------------------------


class TestGetReadingsByWell:
    async def test_returns_readings_for_well(self, client: AsyncClient, session: AsyncSession):
        reading = await _seed_reading(session)
        response = await client.get(f"/readings/well/{reading.well_id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["well_id"] == reading.well_id

    async def test_returns_404_when_no_readings_for_well(self, client: AsyncClient):
        response = await client.get("/readings/well/1000")
        assert response.status_code == 404
        assert response.json()["detail"] == "No readings found for this well"

# ---------------------------------------------------------------------------
# GET /readings/anomalies/{well_id}
# ---------------------------------------------------------------------------


ANOMALOUS_READING_PAYLOAD = {
    **READING_PAYLOAD,
    "temperature_c": 340.0,
}


async def _seed_anomalous_reading(session: AsyncSession) -> Reading:
    well = await _seed_well(session)
    reading = Reading(**ANOMALOUS_READING_PAYLOAD, well_id=well.id)
    session.add(reading)
    await session.commit()
    await session.refresh(reading)
    return reading


class TestGetAnomalies:
    async def test_returns_anomalies_for_well(self, client: AsyncClient, session: AsyncSession):
        reading = await _seed_anomalous_reading(session)
        response = await client.get(f"/readings/anomalies/{reading.well_id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["well_id"] == reading.well_id
        assert data[0]["temperature_c"] == ANOMALOUS_READING_PAYLOAD["temperature_c"]

    async def test_returns_404_when_no_anomalies_for_well(self, client: AsyncClient, session: AsyncSession):
        well = await _seed_well(session)
        # seed a normal
        normal_reading = Reading(
            **{**READING_PAYLOAD, "temperature_c": 50.0},
            well_id=well.id,
        )
        session.add(normal_reading)
        await session.commit()
        response = await client.get(f"/readings/anomalies/{well.id}")
        assert response.status_code == 404
        assert response.json()["detail"] == "No anomalies found for this well"

    async def test_returns_404_when_well_has_no_readings(self, client: AsyncClient):
        response = await client.get("/readings/anomalies/999999")
        assert response.status_code == 404
        assert response.json()["detail"] == "No anomalies found for this well"
