"""Diff generation and comparison engine."""

from sentinel.detector.drift import DriftEvent, DriftSeverity
from sentinel.store.models import SchemaSnapshot


class DiffEngine:
    """Engine for generating human-readable diffs between snapshots."""

    @staticmethod
    def format_event(event: DriftEvent) -> dict:
        """Format a DriftEvent as a dictionary for output.

        Args:
            event: DriftEvent to format

        Returns:
            Dictionary with formatted event data
        """
        return {
            "column": event.column or "(table)",
            "rule": event.rule,
            "severity": event.severity.value,
            "message": event.message,
            "old_value": event.old_value,
            "new_value": event.new_value,
        }

    @staticmethod
    def summary(events: list[DriftEvent]) -> dict[str, int]:
        """Generate summary counts by severity.

        Args:
            events: List of DriftEvents

        Returns:
            Dictionary with counts: {"breaking": N, "warning": N, "info": N}
        """
        summary = {"breaking": 0, "warning": 0, "info": 0}
        for event in events:
            key = event.severity.value.lower()
            summary[key] += 1
        return summary

    @staticmethod
    def has_breaking_changes(events: list[DriftEvent]) -> bool:
        """Check if any breaking changes are present.

        Args:
            events: List of DriftEvents

        Returns:
            True if any BREAKING severity events exist
        """
        return any(e.severity == DriftSeverity.BREAKING for e in events)
