from __future__ import annotations

"""Pytest configuration and shared fixtures."""

import tempfile
from pathlib import Path

import pandas as pd
import pytest

from sentinel.config import SentinelConfig
from sentinel.store.models import ColumnProfile, SchemaSnapshot
from sentinel.core import Sentinel

@pytest.fixture
def temp_db():
    """Temporary database for testing."""

    import sqlite3
    import atexit

    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        # Ensure all connections closed before cleanup
        yield db_path
        # Force garbage collection to close SQLite connections
        import gc
        gc.collect()

@pytest.fixture
def sentinel_config(temp_db):
    """Sentinel config with temporary database."""
    return SentinelConfig(db_path=temp_db)

@pytest.fixture
def sentinel(sentinel_config):
    """Sentinel instance with temporary configuration."""
    return Sentinel(sentinel_config)

@pytest.fixture
def sample_dataframe():
    """Sample DataFrame for testing."""
    return pd.DataFrame({
        "id": [1, 2, 3, 4, 5],
        "name": ["Alice", "Bob", "Charlie", "David", "Eve"],
        "age": [25, 30, 35, 40, 45],
        "active": [True, True, False, True, False],
    })

@pytest.fixture
def sample_snapshot():
    """Sample SchemaSnapshot for testing."""
    return SchemaSnapshot(
        name="test_schema",
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
                sample_values=[100.0, 200.0, 300.0],
            ),
        },
        source_type="pandas",
        version=1,
    )
