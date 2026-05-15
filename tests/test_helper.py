from datetime import datetime

import pytest

from helper.anomaly import (
    GAS_MSCFD_THRESHOLD,
    OIL_BPD_THRESHOLD,
    PRESSURE_PSI_THRESHOLD,
    TEMPERATURE_C_THRESHOLD,
    WATER_BPD_THRESHOLD,
    check_anomalies,
    filter_anomalies_by_type,
)
from models.reading import Reading
from schemas.reading import ReadingResponse

_TS = datetime(2024, 1, 1, 0, 0, 0)


def _make_reading(**kwargs) -> Reading:
    defaults = dict(
        id=1,
        well_id=1,
        timestamp=_TS,
        created_at=_TS,
        pressure_psi=100.0,
        temperature_c=50.0,
        oil_bpd=100.0,
        gas_mscfd=100.0,
        water_bpd=100.0,
    )
    defaults.update(kwargs)
    return Reading(**defaults)


def _make_response(**kwargs) -> ReadingResponse:
    defaults = dict(
        id=1,
        well_id=1,
        timestamp=_TS,
        created_at=_TS,
        pressure_psi=100.0,
        temperature_c=50.0,
        oil_bpd=100.0,
        gas_mscfd=100.0,
        water_bpd=100.0,
    )
    defaults.update(kwargs)
    return ReadingResponse(**defaults)


# ---------------------------------------------------------------------------
# check_anomalies
# ---------------------------------------------------------------------------

class TestCheckAnomalies:
    def test_returns_empty_list_when_no_readings(self):
        assert check_anomalies([]) == []

    def test_returns_empty_list_when_all_readings_are_normal(self):
        readings = [_make_reading(id=1), _make_reading(id=2)]
        assert check_anomalies(readings) == []

    def test_does_not_flag_reading_at_exact_threshold(self):
        reading = _make_reading(pressure_psi=PRESSURE_PSI_THRESHOLD)
        assert check_anomalies([reading]) == []

    def test_detects_pressure_anomaly(self):
        reading = _make_reading(pressure_psi=PRESSURE_PSI_THRESHOLD + 0.1)
        result = check_anomalies([reading])
        assert len(result) == 1
        assert result[0].pressure_psi == reading.pressure_psi

    def test_detects_temperature_anomaly(self):
        reading = _make_reading(temperature_c=TEMPERATURE_C_THRESHOLD + 0.1)
        result = check_anomalies([reading])
        assert len(result) == 1
        assert result[0].temperature_c == reading.temperature_c

    def test_detects_oil_anomaly(self):
        reading = _make_reading(oil_bpd=OIL_BPD_THRESHOLD + 0.1)
        result = check_anomalies([reading])
        assert len(result) == 1
        assert result[0].oil_bpd == reading.oil_bpd

    def test_detects_gas_anomaly(self):
        reading = _make_reading(gas_mscfd=GAS_MSCFD_THRESHOLD + 0.1)
        result = check_anomalies([reading])
        assert len(result) == 1
        assert result[0].gas_mscfd == reading.gas_mscfd

    def test_detects_water_anomaly(self):
        reading = _make_reading(water_bpd=WATER_BPD_THRESHOLD + 0.1)
        result = check_anomalies([reading])
        assert len(result) == 1
        assert result[0].water_bpd == reading.water_bpd

    def test_reading_exceeding_multiple_thresholds_appears_only_once(self):
        reading = _make_reading(
            pressure_psi=PRESSURE_PSI_THRESHOLD + 1,
            temperature_c=TEMPERATURE_C_THRESHOLD + 1,
        )
        result = check_anomalies([reading])
        assert len(result) == 1

    def test_filters_out_normal_readings_among_anomalies(self):
        readings = [
            _make_reading(id=1, pressure_psi=PRESSURE_PSI_THRESHOLD + 1),
            _make_reading(id=2),  # normal
            _make_reading(id=3, temperature_c=TEMPERATURE_C_THRESHOLD + 1),
        ]
        result = check_anomalies(readings)
        assert len(result) == 2
        assert {r.id for r in result} == {1, 3}

    def test_returns_reading_response_objects(self):
        reading = _make_reading(pressure_psi=PRESSURE_PSI_THRESHOLD + 1)
        result = check_anomalies([reading])
        assert isinstance(result[0], ReadingResponse)

    def test_preserves_all_field_values_in_response(self):
        reading = _make_reading(
            id=7,
            well_id=3,
            pressure_psi=PRESSURE_PSI_THRESHOLD + 1,
            temperature_c=30.0,
            oil_bpd=50.0,
            gas_mscfd=200.0,
            water_bpd=80.0,
        )
        result = check_anomalies([reading])
        r = result[0]
        assert r.id == 7
        assert r.well_id == 3
        assert r.oil_bpd == 50.0
        assert r.gas_mscfd == 200.0
        assert r.water_bpd == 80.0


# ---------------------------------------------------------------------------
# filter_anomalies_by_type
# ---------------------------------------------------------------------------

class TestFilterAnomaliesByType:
    def test_returns_empty_list_when_no_anomalies(self):
        assert filter_anomalies_by_type([], "pressure_psi") == []

    def test_returns_empty_for_unknown_type(self):
        anomalies = [_make_response(pressure_psi=PRESSURE_PSI_THRESHOLD + 1)]
        assert filter_anomalies_by_type(anomalies, "unknown_field") == []

    def test_does_not_include_reading_at_exact_threshold(self):
        anomalies = [_make_response(pressure_psi=PRESSURE_PSI_THRESHOLD)]
        assert filter_anomalies_by_type(anomalies, "pressure_psi") == []

    def test_filters_by_pressure_psi(self):
        anomalies = [
            _make_response(id=1, pressure_psi=PRESSURE_PSI_THRESHOLD + 1),
            _make_response(id=2, pressure_psi=100.0),
        ]
        result = filter_anomalies_by_type(anomalies, "pressure_psi")
        assert len(result) == 1
        assert result[0].id == 1

    def test_filters_by_temperature_c(self):
        anomalies = [
            _make_response(id=1, temperature_c=TEMPERATURE_C_THRESHOLD + 1),
            _make_response(id=2, temperature_c=50.0),
        ]
        result = filter_anomalies_by_type(anomalies, "temperature_c")
        assert len(result) == 1
        assert result[0].id == 1

    def test_filters_by_oil_bpd(self):
        anomalies = [
            _make_response(id=1, oil_bpd=OIL_BPD_THRESHOLD + 1),
            _make_response(id=2, oil_bpd=100.0),
        ]
        result = filter_anomalies_by_type(anomalies, "oil_bpd")
        assert len(result) == 1
        assert result[0].id == 1

    def test_filters_by_gas_mscfd(self):
        anomalies = [
            _make_response(id=1, gas_mscfd=GAS_MSCFD_THRESHOLD + 1),
            _make_response(id=2, gas_mscfd=100.0),
        ]
        result = filter_anomalies_by_type(anomalies, "gas_mscfd")
        assert len(result) == 1
        assert result[0].id == 1

    def test_filters_by_water_bpd(self):
        anomalies = [
            _make_response(id=1, water_bpd=WATER_BPD_THRESHOLD + 1),
            _make_response(id=2, water_bpd=100.0),
        ]
        result = filter_anomalies_by_type(anomalies, "water_bpd")
        assert len(result) == 1
        assert result[0].id == 1

    def test_returns_all_readings_exceeding_threshold(self):
        anomalies = [
            _make_response(id=1, pressure_psi=PRESSURE_PSI_THRESHOLD + 1),
            _make_response(id=2, pressure_psi=PRESSURE_PSI_THRESHOLD + 500),
            _make_response(id=3, pressure_psi=100.0),
        ]
        result = filter_anomalies_by_type(anomalies, "pressure_psi")
        assert len(result) == 2
        assert {r.id for r in result} == {1, 2}

    @pytest.mark.parametrize("anomaly_type", [
        "pressure_psi", "temperature_c", "oil_bpd", "gas_mscfd", "water_bpd"
    ])
    def test_all_supported_types_are_handled(self, anomaly_type: str):
        result = filter_anomalies_by_type([], anomaly_type)
        assert result == []
