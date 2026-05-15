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

    async def get_readings_by_well(self, well_id: int) -> list[T]:
        """Return a list of entities associated with a specific well ID."""
        ...

    async def get_anomalies(self, well_id: int) -> list[T]:
        """Return a list of entities that are considered anomalies."""
        ...

    async def get_anomalies_by_type(self, well_id: int) -> list[T]:
        """Returns a list of entities that are considered anomalies, but filtered by the type of anomaly."""
        ...
