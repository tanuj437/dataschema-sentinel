from __future__ import annotations

"""Tests for diff engine."""

import pytest

from sentinel.detector.drift import DriftEvent, DriftSeverity
from sentinel.diff.engine import DiffEngine

@pytest.fixture
def sample_events():
    """Sample drift events for testing."""

    return [
        DriftEvent(
            column="amount",
            rule="TYPE_CHANGED",
            severity=DriftSeverity.BREAKING,
            message="Type changed: float64 → object",
            old_value="float64",
            new_value="object",
        ),
        DriftEvent(
            column="status",
            rule="COLUMN_ADDED",
            severity=DriftSeverity.WARNING,
            message="New column 'status' appeared",
            old_value=None,
            new_value="object",
        ),
        DriftEvent(
            column="id",
            rule="NULLABILITY_CHANGED",
            severity=DriftSeverity.INFO,
            message="Column 'id' now has nulls",
            old_value="False",
            new_value="True",
        ),
    ]

class TestDiffEngine:
    """Tests for DiffEngine."""

    def test_format_event(self, sample_events):
        """Test event formatting."""
        formatted = DiffEngine.format_event(sample_events[0])
        assert formatted["column"] == "amount"
        assert formatted["rule"] == "TYPE_CHANGED"
        assert formatted["severity"] == "BREAKING"

    def test_summary(self, sample_events):
        """Test summary generation."""
        summary = DiffEngine.summary(sample_events)
        assert summary["breaking"] == 1
        assert summary["warning"] == 1
        assert summary["info"] == 1

    def test_has_breaking_changes(self, sample_events):
        """Test detection of breaking changes."""
        assert DiffEngine.has_breaking_changes(sample_events) is True

        # Remove breaking event
        events_no_breaking = [e for e in sample_events if e.severity != DriftSeverity.BREAKING]
        assert DiffEngine.has_breaking_changes(events_no_breaking) is False

    def test_table_level_events(self):
        """Test formatting of table-level events."""
        event = DriftEvent(
            column=None,
            rule="ROW_COUNT_CHANGED",
            severity=DriftSeverity.WARNING,
            message="Row count increased",
            old_value="100",
            new_value="150",
        )
        formatted = DiffEngine.format_event(event)
        assert formatted["column"] == "(table)"

    # TODO: Add more tests for edge cases, sorting, filtering, etc.
