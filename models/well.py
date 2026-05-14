from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Well(SQLModel, table=True):
    __tablename__ = "wells"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    field_name: str
    latitude: float
    longitude: float
    depth_m: float
    status: str = Field(default="active")  # active | inactive | abandoned
    operator: str
    spud_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
