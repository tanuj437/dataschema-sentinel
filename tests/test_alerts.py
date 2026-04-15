"""Tests for alerters."""

import json
from pathlib import Path
from io import StringIO

import pytest
from rich.console import Console

from sentinel.alerts.terminal import TerminalAlerter
from sentinel.alerts.json_alert import JSONAlerter
from sentinel.detector.drift import DriftEvent, DriftSeverity
from sentinel.store.models import ColumnProfile, SchemaSnapshot
import pandas as pd


@pytest.fixture
def snapshots_with_drift():
    """Create snapshots with drift events."""
    snap_v1 = SchemaSnapshot(
        name="test",
        captured_at=pd.Timestamp.utcnow().to_pydatetime(),
        row_count=100,
        columns={
            "id": ColumnProfile(
                name="id",
                dtype="int64",
                nullable=False,
                null_count=0,
                null_pct=0.0,
                unique_count=100,
                min_val=1,
                max_val=100,
                mean_val=50.5,
                sample_values=[1, 2, 3],
            ),
        },
        source_type="pandas",
        version=1,
    )
    snap_v2 = SchemaSnapshot(
        name="test",
        captured_at=pd.Timestamp.utcnow().to_pydatetime(),
        row_count=100,
        columns={
            "id": ColumnProfile(
                name="id",
                dtype="object",  # Type changed
                nullable=False,
                null_count=0,
                null_pct=0.0,
                unique_count=100,
                min_val=None,
                max_val=None,
                mean_val=None,
                sample_values=["1", "2", "3"],
            ),
        },
        source_type="pandas",
        version=2,
    )
    events = [
        DriftEvent(
            column="id",
            rule="TYPE_CHANGED",
            severity=DriftSeverity.BREAKING,
            message="Type changed: int64 → object",
            old_value="int64",
            new_value="object",
        )
    ]
    return snap_v1, snap_v2, events


class TestTerminalAlerter:
    """Tests for TerminalAlerter."""

    def test_alert_with_events(self, snapshots_with_drift):
        """Test rendering alert with events."""
        snap_v1, snap_v2, events = snapshots_with_drift
        output = StringIO()
        console = Console(file=output, width=100)
        alerter = TerminalAlerter(console=console)

        alerter.alert("test", snap_v1, snap_v2, events)
        result = output.getvalue()

        assert "Schema drift detected" in result
        assert "TYPE_CHANGED" in result
        assert "BREAKING" in result

    def test_alert_no_events(self, snapshots_with_drift):
        """Test rendering alert with no events."""
        snap_v1, snap_v2, _ = snapshots_with_drift
        output = StringIO()
        console = Console(file=output, width=100)
        alerter = TerminalAlerter(console=console)

        alerter.alert("test", snap_v1, snap_v2, [])
        result = output.getvalue()

        assert "No schema drift detected" in result


class TestJSONAlerter:
    """Tests for JSONAlerter."""

    def test_alert_to_stdout(self, snapshots_with_drift, capsys):
        """Test writing alert to stdout."""
        snap_v1, snap_v2, events = snapshots_with_drift
        alerter = JSONAlerter()
        alerter.alert("test", snap_v1, snap_v2, events)

        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["schema_name"] == "test"
        assert data["old_version"] == 1
        assert data["new_version"] == 2
        assert len(data["events"]) == 1

    def test_alert_to_file(self, snapshots_with_drift, tmp_path):
        """Test writing alert to file."""
        snap_v1, snap_v2, events = snapshots_with_drift
        output_file = tmp_path / "alert.json"
        alerter = JSONAlerter(output_path=output_file)
        alerter.alert("test", snap_v1, snap_v2, events)

        assert output_file.exists()
        data = json.loads(output_file.read_text())
        assert data["schema_name"] == "test"
        assert data["summary"]["breaking"] == 1

    # TODO: Add more tests for Slack alerter when implemented
