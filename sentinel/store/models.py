"""Core data models for schema snapshots and column profiles."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional


@dataclass
class ColumnProfile:
    """Profile of a single column in a DataFrame/table."""

    name: str
    dtype: str  # Normalized dtype string: "int64", "float64", "object", etc.
    nullable: bool  # True if any nulls observed
    null_count: int
    null_pct: float
    unique_count: Optional[int]  # None for large frames (too expensive)
    min_val: Optional[Any]  # For numeric/date columns
    max_val: Optional[Any]
    mean_val: Optional[float]  # For numeric columns
    sample_values: list[Any] = field(default_factory=list)  # Up to 5 sample values


@dataclass
class SchemaSnapshot:
    """Immutable snapshot of a schema at a point in time."""

    name: str  # Logical name: "orders_df", "public.users", etc.
    captured_at: datetime
    row_count: int
    columns: dict[str, ColumnProfile]  # Keyed by column name
    source_type: str  # "pandas" | "polars" | "sql"
    version: int  # Auto-incremented per name
    tags: dict[str, str] = field(default_factory=dict)  # Arbitrary metadata

    def to_dict(self) -> dict[str, Any]:
        """Serialize snapshot to dictionary."""
        return {
            "name": self.name,
            "captured_at": self.captured_at.isoformat(),
            "row_count": self.row_count,
            "source_type": self.source_type,
            "version": self.version,
            "columns": {k: self._column_to_dict(v) for k, v in self.columns.items()},
            "tags": self.tags,
        }

    @staticmethod
    def _column_to_dict(col: ColumnProfile) -> dict[str, Any]:
        """Convert ColumnProfile to dictionary."""
        return {
            "name": col.name,
            "dtype": col.dtype,
            "nullable": col.nullable,
            "null_count": col.null_count,
            "null_pct": col.null_pct,
            "unique_count": col.unique_count,
            "min_val": col.min_val,
            "max_val": col.max_val,
            "mean_val": col.mean_val,
            "sample_values": col.sample_values,
        }
