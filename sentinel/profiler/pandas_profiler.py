"""Profiler for pandas DataFrames."""

from datetime import datetime, timezone
from typing import Any, Optional

import pandas as pd

from sentinel.profiler.base import BaseProfiler
from sentinel.store.models import ColumnProfile, SchemaSnapshot


DTYPE_MAP = {
    "int64": "int64",
    "int32": "int64",
    "int16": "int64",
    "int8": "int64",
    "uint64": "int64",
    "uint32": "int64",
    "uint16": "int64",
    "uint8": "int64",
    "float64": "float64",
    "float32": "float64",
    "float16": "float64",
    "bool": "bool",
    "object": "object",
    "string": "object",  # Normalize pandas StringDtype to object
    "str": "object",  # Handle string alias
    "datetime64[ns]": "datetime",
    "datetime64[ns, UTC]": "datetime",
    "category": "category",
}


class PandasProfiler(BaseProfiler):
    """Profiler for pandas DataFrames."""

    def profile(self, df: pd.DataFrame, name: str, version: int) -> SchemaSnapshot:
        """Profile a pandas DataFrame.

        Args:
            df: DataFrame to profile
            name: Logical name
            version: Version number

        Returns:
            SchemaSnapshot
        """
        if not isinstance(df, pd.DataFrame):
            raise TypeError(f"Expected pd.DataFrame, got {type(df)}")

        columns = {}
        for col in df.columns:
            series = df[col]
            dtype_str = self._normalize_dtype(str(series.dtype))
            null_count = int(series.isna().sum())
            null_pct = round(null_count / max(len(df), 1) * 100, 2)

            # Numeric stats
            mean_val = None
            min_val = None
            max_val = None
            if pd.api.types.is_numeric_dtype(series):
                non_null = series.dropna()
                if len(non_null) > 0:
                    mean_val = float(non_null.mean())
                    min_val = float(non_null.min())
                    max_val = float(non_null.max())
            elif pd.api.types.is_datetime64_any_dtype(series):
                non_null = series.dropna()
                if len(non_null) > 0:
                    min_val = str(non_null.min())
                    max_val = str(non_null.max())

            # Unique count — skip for large high-cardinality columns
            unique_count = None
            if len(df) <= 100_000:
                unique_count = int(series.nunique())

            columns[col] = ColumnProfile(
                name=col,
                dtype=dtype_str,
                nullable=null_count > 0,
                null_count=null_count,
                null_pct=null_pct,
                unique_count=unique_count,
                min_val=min_val,
                max_val=max_val,
                mean_val=mean_val,
                sample_values=series.dropna().head(5).tolist(),
            )

        return SchemaSnapshot(
            name=name,
            captured_at=datetime.now(timezone.utc),
            row_count=len(df),
            columns=columns,
            source_type="pandas",
            version=version,
        )

    @staticmethod
    def _normalize_dtype(dtype_str: str) -> str:
        """Normalize pandas dtype to standard string format."""
        # Handle complex types like datetime64[ns, UTC]
        base_dtype = dtype_str.split("[")[0] if "[" in dtype_str else dtype_str
        return DTYPE_MAP.get(base_dtype, dtype_str)
