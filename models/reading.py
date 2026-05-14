from datetime import datetime
from typing import Optional

from sqlmodel import Field, Float, SQLModel


class Reading(SQLModel, table=True):
    __tablename__ = "readings"
    id: Optional[int] = Field(default=None, primary_key=True)
    well_id: int = Field(foreign_key="wells.id")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    pressure_psi: float
    temperature_c: float
    created_at: datetime = Field(default_factory=datetime.utcnow)
    oil_bpd: float = Field(sa_column=Float)
    gas_mscfd: float = Field(sa_column=Float)
    water_bpd: float = Field(sa_column=Float)
