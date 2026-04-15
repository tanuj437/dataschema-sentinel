from __future__ import annotations

"""Base class for schema profilers."""

from abc import ABC, abstractmethod
from sentinel.store.models import SchemaSnapshot

class BaseProfiler(ABC):
    """Abstract base class for schema profilers."""

    @abstractmethod
    def profile(self, source: any, name: str, version: int) -> SchemaSnapshot:
        """Profile a data source and return a SchemaSnapshot.

        Args:
            source: Data source (DataFrame, table name, etc.)
            name: Logical name for the snapshot
            version: Version number

        Returns:
            SchemaSnapshot with profiled schema
        """
        pass
