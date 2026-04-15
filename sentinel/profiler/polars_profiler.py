"""Profiler for Polars DataFrames."""

from datetime import datetime

from sentinel.profiler.base import BaseProfiler
from sentinel.store.models import SchemaSnapshot


class PolarsProfiler(BaseProfiler):
    """Profiler for Polars DataFrames.

    TODO: Implement Polars DataFrame profiling.
    """

    def profile(self, df, name: str, version: int) -> SchemaSnapshot:
        """Profile a Polars DataFrame.

        Args:
            df: Polars DataFrame to profile
            name: Logical name
            version: Version number

        Returns:
            SchemaSnapshot
        """
        raise NotImplementedError("PolarsProfiler not yet implemented")
