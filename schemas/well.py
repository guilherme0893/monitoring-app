from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

"""Basic DTOs for the well entity, used for request validation and response formatting."""


class WellCreate(BaseModel):
    """Payload expected when creating a new well."""
    name: str
    field_name: str
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    depth_m: float = Field(gt=0)
    status: str = "active"
    operator: str
    spud_date: Optional[datetime] = None
    type_id: int


class WellUpdate(BaseModel):
    """All fields optional — only provided fields will be updated."""
    name: Optional[str] = None
    field_name: Optional[str] = None
    latitude: Optional[float] = Field(default=None, ge=-90, le=90)
    longitude: Optional[float] = Field(default=None, ge=-180, le=180)
    depth_m: Optional[float] = Field(default=None, gt=0)
    status: Optional[str] = None
    operator: Optional[str] = None
    spud_date: Optional[datetime] = None


class WellResponse(BaseModel):
    """Shape of a well returned by the API."""
    id: int
    name: str
    field_name: str
    latitude: float
    longitude: float
    depth_m: float
    status: str
    operator: str
    spud_date: Optional[datetime]
    created_at: datetime
    type_id: int

    model_config = {"from_attributes": True}
