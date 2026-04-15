"""Tests for schema storage."""

import pytest

from sentinel.store.schema_store import SchemaStore


class TestSchemaStore:
    """Tests for SchemaStore."""
from __future__ import annotations


    def test_save_and_load_latest(self, temp_db, sample_snapshot):
        """Test saving and loading latest snapshot."""
        store = SchemaStore(temp_db)
        version = store.save(sample_snapshot)

        assert version == 1
        loaded = store.load_latest("test_schema")
        assert loaded is not None
        assert loaded.name == "test_schema"
        assert loaded.version == 1
        assert loaded.row_count == 100

    def test_version_auto_increment(self, temp_db, sample_snapshot):
        """Test that versions auto-increment."""
        store = SchemaStore(temp_db)
        v1 = store.save(sample_snapshot)
        assert v1 == 1

        sample_snapshot.version = 2
        v2 = store.save(sample_snapshot)
        assert v2 == 2

    def test_load_version(self, temp_db, sample_snapshot):
        """Test loading a specific version."""
        store = SchemaStore(temp_db)
        store.save(sample_snapshot)

        loaded = store.load_version("test_schema", 1)
        assert loaded is not None
        assert loaded.version == 1

        not_found = store.load_version("test_schema", 99)
        assert not_found is None

    def test_history(self, temp_db, sample_snapshot):
        """Test loading snapshot history."""
        store = SchemaStore(temp_db)
        store.save(sample_snapshot)
        sample_snapshot.version = 2
        store.save(sample_snapshot)
        sample_snapshot.version = 3
        store.save(sample_snapshot)

        history = store.history("test_schema", last_n=2)
        assert len(history) == 2
        assert history[0].version == 3
        assert history[1].version == 2

    def test_list_schemas(self, temp_db, sample_snapshot):
        """Test listing all tracked schemas."""
        store = SchemaStore(temp_db)
        store.save(sample_snapshot)

        sample_snapshot.name = "another_schema"
        store.save(sample_snapshot)

        schemas = store.list_schemas()
        assert "test_schema" in schemas
        assert "another_schema" in schemas

    # TODO: Add more tests for concurrent access, serialization, etc.
