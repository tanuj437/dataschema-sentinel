from __future__ import annotations

"""Base class for alerters."""

from abc import ABC, abstractmethod
from typing import Optional

from sentinel.detector.drift import DriftEvent
from sentinel.store.models import SchemaSnapshot

class BaseAlerter(ABC):
    """Abstract base class for drift alerters."""

    @abstractmethod
    def alert(
        self,
        name: str,
        old_snapshot: SchemaSnapshot,
        new_snapshot: SchemaSnapshot,
        events: list[DriftEvent],
    ) -> None:
        """Send an alert about detected drift.

        Args:
            name: Schema name
            old_snapshot: Previous snapshot
            new_snapshot: Current snapshot
            events: List of drift events
        """
        pass
