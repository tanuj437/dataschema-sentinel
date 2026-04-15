"""DataSchema Sentinel - Zero-config schema drift detection for data pipelines."""

from sentinel.config import SentinelConfig
from sentinel.core import Sentinel, SchemaDriftError
from sentinel.detector import DriftEvent, DriftSeverity, rule
from sentinel.store import ColumnProfile, SchemaSnapshot

# Global singleton instance
_sentinel_instance = Sentinel()


def watch(name: str, on_drift: str = "warn", profiler_type: str = "pandas"):
    """Decorator to watch a function for schema drift.
from __future__ import annotations


    Args:
        name: Logical name for the schema
        on_drift: Action on drift ("warn", "raise", "log", "alert")
        profiler_type: Profiler type ("pandas", "polars", "sql")

    Returns:
        Decorator function

    Example:
        @sentinel.watch("orders", on_drift="raise")
        def load_orders() -> pd.DataFrame:
            return pd.read_csv("orders.csv")
    """
    return _sentinel_instance.watch(name, on_drift, profiler_type)


def wrap(df, name: str, on_drift: str = "warn", profiler_type: str = "pandas"):
    """Wrap a DataFrame to track schema changes.

    Args:
        df: DataFrame to wrap
        name: Logical name for the schema
        on_drift: Action on drift
        profiler_type: Profiler type

    Returns:
        Original DataFrame

    Example:
        df = sentinel.wrap(df, name="data", on_drift="raise")
    """
    return _sentinel_instance.wrap(df, name, on_drift, profiler_type)


def compare(name: str):
    """Context manager for explicit schema comparison.

    Args:
        name: Schema name

    Returns:
        Context manager

    Example:
        with sentinel.compare("users") as ctx:
            df = pd.read_sql("SELECT * FROM users", engine)
            ctx.check(df)
    """
    return _sentinel_instance.compare(name)


def configure(config: SentinelConfig) -> None:
    """Configure Sentinel with custom settings.

    Args:
        config: SentinelConfig instance
    """
    global _sentinel_instance
    _sentinel_instance = Sentinel(config)


def get_instance() -> Sentinel:
    """Get the global Sentinel instance.

    Returns:
        Sentinel instance
    """
    return _sentinel_instance


__version__ = "0.1.0"
__all__ = [
    "watch",
    "wrap",
    "compare",
    "configure",
    "get_instance",
    "Sentinel",
    "SchemaDriftError",
    "DriftEvent",
    "DriftSeverity",
    "SchemaSnapshot",
    "ColumnProfile",
    "SentinelConfig",
    "rule",
]
