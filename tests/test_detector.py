from __future__ import annotations

"""Tests for drift detection."""

import pytest

from sentinel.detector.drift import (
    DriftSeverity,
    detect_drift,
    _check_dropped_columns,
    _check_added_columns,
    _check_type_changes,
)
from sentinel.store.models import ColumnProfile, SchemaSnapshot
import pandas as pd

@pytest.fixture
def snapshot_v1():
    """First version of a schema."""

    return SchemaSnapshot(
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
            "amount": ColumnProfile(
                name="amount",
                dtype="float64",
                nullable=False,
                null_count=0,
                null_pct=0.0,
                unique_count=95,
                min_val=10.5,
                max_val=500.0,
                mean_val=250.0,
                sample_values=[100.0],
            ),
        },
        source_type="pandas",
        version=1,
    )

class TestDriftDetection:
    """Tests for drift detection."""

    def test_no_drift_identical_snapshots(self, snapshot_v1):
        """Test no drift when snapshots are identical."""
        events = detect_drift(snapshot_v1, snapshot_v1)
        assert len(events) == 0

    def test_detect_column_dropped(self, snapshot_v1):
        """Test detection of dropped columns."""
        snapshot_v2 = SchemaSnapshot(
            name="test",
            captured_at=pd.Timestamp.utcnow().to_pydatetime(),
            row_count=100,
            columns={"id": snapshot_v1.columns["id"]},
            source_type="pandas",
            version=2,
        )
        events = detect_drift(snapshot_v1, snapshot_v2)
        assert len(events) == 1
        assert events[0].rule == "COLUMN_DROPPED"
        assert events[0].column == "amount"
        assert events[0].severity == DriftSeverity.BREAKING

    def test_detect_column_added(self, snapshot_v1):
        """Test detection of added columns."""
        new_col = ColumnProfile(
            name="status",
            dtype="object",
            nullable=True,
            null_count=5,
            null_pct=5.0,
            unique_count=3,
            min_val=None,
            max_val=None,
            mean_val=None,
            sample_values=["active", "inactive"],
        )
        snapshot_v2 = SchemaSnapshot(
            name="test",
            captured_at=pd.Timestamp.utcnow().to_pydatetime(),
            row_count=100,
            columns={**snapshot_v1.columns, "status": new_col},
            source_type="pandas",
            version=2,
        )
        events = detect_drift(snapshot_v1, snapshot_v2)
        assert len(events) == 1
        assert events[0].rule == "COLUMN_ADDED"
        assert events[0].column == "status"
        assert events[0].severity == DriftSeverity.WARNING

    def test_detect_type_change(self, snapshot_v1):
        """Test detection of type changes."""
        modified_amount = ColumnProfile(
            name="amount",
            dtype="object",  # Changed from float64
            nullable=False,
            null_count=0,
            null_pct=0.0,
            unique_count=95,
            min_val=None,
            max_val=None,
            mean_val=None,
            sample_values=["100.0"],
        )
        snapshot_v2 = SchemaSnapshot(
            name="test",
            captured_at=pd.Timestamp.utcnow().to_pydatetime(),
            row_count=100,
            columns={"id": snapshot_v1.columns["id"], "amount": modified_amount},
            source_type="pandas",
            version=2,
        )
        events = detect_drift(snapshot_v1, snapshot_v2)
        assert len(events) == 1
        assert events[0].rule == "TYPE_CHANGED"
        assert events[0].severity == DriftSeverity.BREAKING

    def test_detect_nullability_change(self, snapshot_v1):
        """Test detection of nullability changes."""
        # Create a new ColumnProfile (don't mutate the fixture)
        modified_amount = ColumnProfile(
            name="amount",
            dtype="float64",
            nullable=True,  # Changed from False
            null_count=10,
            null_pct=10.0,
            unique_count=95,
            min_val=10.5,
            max_val=500.0,
            mean_val=250.0,
            sample_values=[100.0],
        )

        snapshot_v2 = SchemaSnapshot(
            name="test",
            captured_at=pd.Timestamp.utcnow().to_pydatetime(),
            row_count=100,
            columns={"id": snapshot_v1.columns["id"], "amount": modified_amount},
            source_type="pandas",
            version=2,
        )
        events = detect_drift(snapshot_v1, snapshot_v2)
        assert len(events) == 1
        assert events[0].rule == "NULLABILITY_CHANGED"
        assert events[0].severity == DriftSeverity.WARNING

    def test_detect_row_count_change(self, snapshot_v1):
        """Test detection of row count changes."""
        snapshot_v2 = SchemaSnapshot(
            name="test",
            captured_at=pd.Timestamp.utcnow().to_pydatetime(),
            row_count=150,  # 50% increase
            columns=snapshot_v1.columns,
            source_type="pandas",
            version=2,
        )
        events = detect_drift(snapshot_v1, snapshot_v2)
        assert len(events) == 1
        assert events[0].rule == "ROW_COUNT_CHANGED"
        assert events[0].severity == DriftSeverity.WARNING

    # TODO: Add more tests for stats drift, multiple events, rule filtering, etc.
