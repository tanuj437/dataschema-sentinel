"""Profiler for SQL tables via SQLAlchemy."""

from datetime import datetime, timezone

from sentinel.profiler.base import BaseProfiler
from sentinel.store.models import SchemaSnapshot


class SQLProfiler(BaseProfiler):
    """Profiler for SQL tables via SQLAlchemy.

    TODO: Implement SQL table profiling via information_schema.
    """

    def profile(self, engine, table_name: str, name: str, version: int) -> SchemaSnapshot:
        """Profile a SQL table.

        Args:
            engine: SQLAlchemy engine
            table_name: Table to profile
            name: Logical name
            version: Version number

        Returns:
            SchemaSnapshot
        """
        raise NotImplementedError("SQLProfiler not yet implemented")
