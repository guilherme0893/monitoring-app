from models.reading import Reading
from schemas.reading import ReadingResponse

PRESSURE_PSI_THRESHOLD = 5000.0
TEMPERATURE_C_THRESHOLD = 120.0
OIL_BPD_THRESHOLD = 1000.0
GAS_MSCFD_THRESHOLD = 5000.0
WATER_BPD_THRESHOLD = 1500.0


def check_anomalies(readings: list[Reading]) -> list[ReadingResponse]:
    anomalies: list[ReadingResponse] = []

    for reading in readings:
        is_anomaly = (
            reading.pressure_psi > PRESSURE_PSI_THRESHOLD
            or reading.temperature_c > TEMPERATURE_C_THRESHOLD
            or reading.oil_bpd > OIL_BPD_THRESHOLD
            or reading.gas_mscfd > GAS_MSCFD_THRESHOLD
            or reading.water_bpd > WATER_BPD_THRESHOLD
        )

        if is_anomaly:
            anomalies.append(ReadingResponse(
                id=reading.id,
                well_id=reading.well_id,
                timestamp=reading.timestamp,
                pressure_psi=reading.pressure_psi,
                temperature_c=reading.temperature_c,
                oil_bpd=reading.oil_bpd,
                gas_mscfd=reading.gas_mscfd,
                water_bpd=reading.water_bpd,
                created_at=reading.created_at
            ))

    return anomalies


ANOMALY_TYPE_THRESHOLDS: dict[str, tuple[str, float]] = {
    "pressure_psi": ("pressure_psi", PRESSURE_PSI_THRESHOLD),
    "temperature_c": ("temperature_c", TEMPERATURE_C_THRESHOLD),
    "oil_bpd": ("oil_bpd", OIL_BPD_THRESHOLD),
    "gas_mscfd": ("gas_mscfd", GAS_MSCFD_THRESHOLD),
    "water_bpd": ("water_bpd", WATER_BPD_THRESHOLD),
}


def filter_anomalies_by_type(anomalies: list[ReadingResponse], anomaly_type: str) -> list[ReadingResponse]:
    threshold_info = ANOMALY_TYPE_THRESHOLDS.get(anomaly_type)
    if threshold_info is None:
        return []

    field, threshold = threshold_info
    return [anomaly for anomaly in anomalies if getattr(anomaly, field) > threshold]
