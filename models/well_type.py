import enum
from typing import Optional

import sqlalchemy as sa
from sqlmodel import Column, Field, SQLModel


class WellTypeEnum(str, enum.Enum):
    producer = "producer"
    injector = "injector"


class WellType(SQLModel, table=True):
    __tablename__ = "well_types"
    id: Optional[int] = Field(default=None, primary_key=True)
    type: WellTypeEnum = Field(
        sa_column=Column(sa.Enum(WellTypeEnum), nullable=False, index=True)
    )
