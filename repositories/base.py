from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @abstractmethod
    async def get_all(self) -> list[T]:
        """Return all records of type T."""
        ...

    @abstractmethod
    async def get_by_id(self, id: int) -> Optional[T]:
        """Return a single record by primary key, or None."""
        ...
