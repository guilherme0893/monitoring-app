from unittest.mock import AsyncMock, MagicMock

from helper.anomaly import check_anomalies
from models.reading import Reading
from repositories.reading_repository import ReadingRepository
from services.reading_service import ReadingService


def _make_reading(**kwargs) -> Reading:
    defaults = dict(
        id=1,
        well_id=1,
        timestamp="2024-01-01T00:00:00Z",
        pressure_psi=3000.0,
        temperature_c=150.0,
        oil_bpd=500.0,
        gas_mscfd=2000.0,
        water_bpd=100.0,
    )
    defaults.update(kwargs)
    return Reading(**defaults)


def _make_service(repo: ReadingRepository) -> ReadingService:
    return ReadingService(repo)


class TestGetAll:
    async def test_returns_all_readings_from_repository(self):
        readings = [_make_reading(id=1), _make_reading(id=2, pressure_psi=3200.0)]
        repo = MagicMock(spec=ReadingRepository)
        repo.get_all = AsyncMock(return_value=readings)
        service = _make_service(repo)

        result = await service.get_all()

        repo.get_all.assert_awaited_once()
        assert result == readings

    async def test_returns_empty_list_when_no_readings(self):
        repo = MagicMock(spec=ReadingRepository)
        repo.get_all = AsyncMock(return_value=[])
        service = _make_service(repo)

        result = await service.get_all()

        assert result == []


class TestGetById:
    async def test_return_reading_when_found(self):
        reading = _make_reading(id=42)
        repo = MagicMock(spec=ReadingRepository)
        repo.get_by_id = AsyncMock(return_value=reading)
        service = _make_service(repo)

        result = await service.get_by_id(42)

        repo.get_by_id.assert_awaited_once_with(42)
        assert result == reading

    async def test_return_none_when_not_found(self):
        repo = MagicMock(spec=ReadingRepository)
        repo.get_by_id = AsyncMock(return_value=None)
        service = _make_service(repo)

        result = await service.get_by_id(999)

        repo.get_by_id.assert_awaited_once_with(999)
        assert result is None


class TestGetReadingByWell:
    async def test_return_readings_for_well(self):
        readings = [_make_reading(id=1, well_id=10), _make_reading(id=2, well_id=10)]
        repo = MagicMock(spec=ReadingRepository)
        repo.get_readings_by_well = AsyncMock(return_value=readings)
        service = _make_service(repo)

        result = await service.get_readings_by_well(10)

        repo.get_readings_by_well.assert_awaited_once_with(10)
        assert result == readings

    async def test_return_empty_list_when_no_readings_for_well(self):
        repo = MagicMock(spec=ReadingRepository)
        repo.get_readings_by_well = AsyncMock(return_value=[])
        service = _make_service(repo)

        result = await service.get_readings_by_well(999)

        repo.get_readings_by_well.assert_awaited_once_with(999)
        assert result == []


class TestGetAnomalies:
    async def test_return_anomalies_for_well(self):
        readings = [_make_reading(id=1, well_id=10), _make_reading(id=2, well_id=10, temperature_c=340)]
        repo = MagicMock(spec=ReadingRepository)
        repo.get_readings_by_well = AsyncMock(return_value=readings)
        service = _make_service(repo)

        result = await service.get_anomalies(10)

        repo.get_readings_by_well.assert_awaited_once_with(10)
        assert result == check_anomalies(readings)

    async def test_return_empty_when_no_anomalies_for_well(self):
        readings = [
            _make_reading(id=1, well_id=10, temperature_c=100.0),
            _make_reading(id=2, well_id=10, temperature_c=100.0),
        ]
        repo = MagicMock(spec=ReadingRepository)
        repo.get_readings_by_well = AsyncMock(return_value=readings)

        service = _make_service(repo)

        result = await service.get_anomalies(10)

        repo.get_readings_by_well.assert_awaited_once_with(10)
        assert result == []

