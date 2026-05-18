import io
import openpyxl


def export_as_xlsx(anomalies: list, well_id: int) -> io.BytesIO:
    if not anomalies:
        return io.BytesIO()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"Anomalies - Well {well_id}"

    headers = ["id", "well_id", "timestamp", "pressure_psi", "temperature_c", "oil_bpd", "gas_mscfd", "water_bpd", "created_at"]
    ws.append(headers)

    for r in anomalies:
        ws.append([
            r.id,
            r.well_id,
            r.timestamp.isoformat(),
            r.pressure_psi,
            r.temperature_c,
            r.oil_bpd,
            r.gas_mscfd,
            r.water_bpd,
            r.created_at.isoformat(),
        ])

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer
