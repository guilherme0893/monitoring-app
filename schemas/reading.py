from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ReadingCreate(BaseModel):
    """Payload expected when creating a new reading."""
    well_id: int
    timestamp: Optional[datetime] = None
    pressure_psi: float
    temperature_c: float
    oil_bpd: float
    gas_mscfd: float
    water_bpd: float


class ReadingResponse(BaseModel):
    """Shape of a reading returned by the API."""
    id: int
    well_id: int
    timestamp: datetime
    pressure_psi: float
    temperature_c: float
    oil_bpd: float
    gas_mscfd: float
    water_bpd: float
    created_at: datetime

    model_config = {"from_attributes": True}
