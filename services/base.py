from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar

T = TypeVar("T")


class BaseService(ABC, Generic[T]):
    @abstractmethod
    async def get_all(self) -> list[T]:
        """Return all entities of type T."""
        ...

    @abstractmethod
    async def get_by_id(self, id: int) -> Optional[T]:
        """Return a single entity by ID, or None if not found."""
        ...
