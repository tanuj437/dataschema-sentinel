"""Tests for profillers."""

import pandas as pd
import pytest

from sentinel.profiler.pandas_profiler import PandasProfiler


class TestPandasProfiler:
    """Tests for PandasProfiler."""

    def test_profile_basic_dataframe(self, sample_dataframe):
        """Test profiling a basic DataFrame."""
        profiler = PandasProfiler()
        snapshot = profiler.profile(sample_dataframe, "test", 1)

        assert snapshot.name == "test"
        assert snapshot.version == 1
        assert snapshot.row_count == 5
        assert snapshot.source_type == "pandas"
        assert len(snapshot.columns) == 4
        assert "id" in snapshot.columns
        assert "name" in snapshot.columns

    def test_profile_dtype_normalization(self):
        """Test dtype normalization."""
        df = pd.DataFrame({
            "int_col": pd.array([1, 2, 3], dtype="int64"),
            "float_col": pd.array([1.0, 2.0, 3.0], dtype="float64"),
            "str_col": ["a", "b", "c"],
        })
        profiler = PandasProfiler()
        snapshot = profiler.profile(df, "test", 1)

        assert snapshot.columns["int_col"].dtype == "int64"
        assert snapshot.columns["float_col"].dtype == "float64"
        assert snapshot.columns["str_col"].dtype == "object"

    def test_profile_with_nulls(self):
        """Test profiling a DataFrame with null values."""
        df = pd.DataFrame({
            "col_with_nulls": [1, 2, None, 4, 5],
            "col_no_nulls": [1, 2, 3, 4, 5],
        })
        profiler = PandasProfiler()
        snapshot = profiler.profile(df, "test", 1)

        assert snapshot.columns["col_with_nulls"].nullable is True
        assert snapshot.columns["col_with_nulls"].null_count == 1
        assert snapshot.columns["col_no_nulls"].nullable is False
        assert snapshot.columns["col_no_nulls"].null_count == 0

    def test_profile_numeric_stats(self):
        """Test numeric statistics calculation."""
        df = pd.DataFrame({
            "values": [10.0, 20.0, 30.0, 40.0, 50.0],
        })
        profiler = PandasProfiler()
        snapshot = profiler.profile(df, "test", 1)

        col = snapshot.columns["values"]
        assert col.min_val == 10.0
        assert col.max_val == 50.0
        assert col.mean_val == 30.0

    # TODO: Add more tests for edge cases, error handling, etc.
