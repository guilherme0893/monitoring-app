from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from models.well import Well


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

WELL_PAYLOAD = {
    "name": "Well-Alpha",
    "field_name": "North Field",
    "latitude": -22.9,
    "longitude": -43.1,
    "depth_m": 3500.0,
    "status": "active",
    "operator": "PetroCorp",
}


async def _seed_well(session: AsyncSession) -> Well:
    well = Well(**WELL_PAYLOAD)
    session.add(well)
    await session.commit()
    await session.refresh(well)
    return well


# ---------------------------------------------------------------------------
# GET /wells/
# ---------------------------------------------------------------------------

class TestGetWells:
    async def test_returns_empty_list_when_no_wells(self, client: AsyncClient, session: AsyncSession):
        response = await client.get("/wells/")
        assert response.status_code == 200
        assert response.json() == []

    async def test_returns_list_with_seeded_well(self, client: AsyncClient, session: AsyncSession):
        await _seed_well(session)
        response = await client.get("/wells/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["name"] == WELL_PAYLOAD["name"]


# ---------------------------------------------------------------------------
# GET /wells/{well_id}
# ---------------------------------------------------------------------------

class TestGetWellById:
    async def test_returns_well_when_found(self, client: AsyncClient, session: AsyncSession):
        well = await _seed_well(session)
        response = await client.get(f"/wells/{well.id}")
        assert response.status_code == 200
        body = response.json()
        assert body["id"] == well.id
        assert body["name"] == well.name
        assert body["field_name"] == well.field_name
        assert body["operator"] == well.operator

    async def test_returns_404_when_not_found(self, client: AsyncClient):
        response = await client.get("/wells/999999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Well not found"

    async def test_response_schema_has_required_fields(self, client: AsyncClient, session: AsyncSession):
        well = await _seed_well(session)
        response = await client.get(f"/wells/{well.id}")
        body = response.json()
        for field in (
            "id",
            "name",
            "field_name",
            "latitude",
            "longitude",
            "depth_m",
            "status",
            "operator",
            "created_at",
        ):
            assert field in body, f"Missing field: {field}"
