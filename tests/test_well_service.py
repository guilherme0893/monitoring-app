from unittest.mock import AsyncMock, MagicMock

from models.well import Well
from repositories.well_repository import WellRepository
from services.well_service import WellService


def _make_well(**kwargs) -> Well:
    defaults = dict(
        id=1,
        name="Well-Beta",
        field_name="South Field",
        latitude=10.0,
        longitude=-60.0,
        depth_m=2000.0,
        status="active",
        operator="DrillCo",
        spud_date=None,
    )
    defaults.update(kwargs)
    return Well(**defaults)


def _make_service(repo: WellRepository) -> WellService:
    return WellService(repo)


# ---------------------------------------------------------------------------
# WellService.get_all
# ---------------------------------------------------------------------------

class TestGetAll:
    async def test_returns_all_wells_from_repository(self):
        wells = [_make_well(id=1), _make_well(id=2, name="Well-Gamma")]
        repo = MagicMock(spec=WellRepository)
        repo.get_all = AsyncMock(return_value=wells)
        service = _make_service(repo)

        result = await service.get_all()

        repo.get_all.assert_awaited_once()
        assert result == wells

    async def test_returns_empty_list_when_no_wells(self):
        repo = MagicMock(spec=WellRepository)
        repo.get_all = AsyncMock(return_value=[])
        service = _make_service(repo)

        result = await service.get_all()

        assert result == []


# ---------------------------------------------------------------------------
# WellService.get_by_id
# ---------------------------------------------------------------------------

class TestGetById:
    async def test_returns_well_when_found(self):
        well = _make_well(id=42)
        repo = MagicMock(spec=WellRepository)
        repo.get_by_id = AsyncMock(return_value=well)
        service = _make_service(repo)

        result = await service.get_by_id(42)

        repo.get_by_id.assert_awaited_once_with(42)
        assert result is well

    async def test_returns_none_when_not_found(self):
        repo = MagicMock(spec=WellRepository)
        repo.get_by_id = AsyncMock(return_value=None)
        service = _make_service(repo)

        result = await service.get_by_id(999)

        assert result is None
