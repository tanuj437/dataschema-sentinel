"""Main Sentinel class for schema drift detection."""

from __future__ import annotations

from datetime import datetime
from functools import wraps
from typing import Any, Callable, Literal, Optional, TypeVar

from sentinel.alerts.base import BaseAlerter
from sentinel.alerts.terminal import TerminalAlerter
from sentinel.config import SentinelConfig
from sentinel.detector.drift import detect_drift
from sentinel.profiler.base import BaseProfiler
from sentinel.profiler.pandas_profiler import PandasProfiler
from sentinel.store.models import SchemaSnapshot
from sentinel.store.schema_store import SchemaStore


T = TypeVar("T")


class SchemaDriftError(Exception):
    """Raised when schema drift is detected with on_drift='raise'."""

    pass


class Sentinel:
    """Main class for schema drift detection."""

    def __init__(self, config: SentinelConfig | None = None):
        """Initialize Sentinel.

        Args:
            config: SentinelConfig instance (creates default if None)
        """
        self.config = config or SentinelConfig()
        self.store = SchemaStore(self.config.db_path)
        self.profilers: dict[str, BaseProfiler] = {
            "pandas": PandasProfiler(),
        }
        self.alerter: Optional[BaseAlerter] = TerminalAlerter()

    def set_alerter(self, alerter: BaseAlerter) -> None:
        """Set the alerter for drift notifications.

        Args:
            alerter: BaseAlerter instance
        """
        self.alerter = alerter

    def watch(
        self,
        name: str,
        on_drift: Literal["warn", "raise", "log", "alert"] = "warn",
        profiler_type: str = "pandas",
    ) -> Callable:
        """Decorator to watch a function that returns a DataFrame.

        Args:
            name: Logical name for the schema
            on_drift: Action on detected drift ("warn", "raise", "log", "alert")
            profiler_type: Type of profiler to use ("pandas", "polars", "sql")

        Returns:
            Decorator function

        Example:
            @sentinel.watch("orders_df", on_drift="raise")
            def load_orders() -> pd.DataFrame:
                return pd.read_csv("orders.csv")
        """

        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            @wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> T:
                df = func(*args, **kwargs)
                self.wrap(df, name=name, on_drift=on_drift, profiler_type=profiler_type)
                return df

            return wrapper

        return decorator

    def wrap(
        self,
        df: Any,
        name: str,
        on_drift: Literal["warn", "raise", "log", "alert"] = "warn",
        profiler_type: str = "pandas",
    ) -> Any:
        """Wrap a DataFrame to track schema changes.

        Args:
            df: DataFrame to wrap
            name: Logical name for the schema
            on_drift: Action on detected drift
            profiler_type: Type of profiler to use

        Returns:
            Original DataFrame (unchanged)

        Example:
            df = pd.read_csv("data.csv")
            df = sentinel.wrap(df, name="data", on_drift="raise")
        """
        profiler = self.profilers.get(profiler_type)
        if not profiler:
            raise ValueError(f"Unknown profiler type: {profiler_type}")

        # Get the next version number
        latest = self.store.load_latest(name)
        version = (latest.version + 1) if latest else 1

        # Profile the current data
        new_snapshot = profiler.profile(df, name, version)

        # Compare with previous snapshot
        if latest:
            events = detect_drift(
                latest,
                new_snapshot,
                rules=self.config.enabled_rules,
                row_count_threshold=self.config.row_count_threshold,
                stats_drift_threshold=self.config.stats_drift_threshold,
            )

            if events:
                self._handle_drift(name, latest, new_snapshot, events, on_drift)

        # Save the current snapshot
        self.store.save(new_snapshot)

        return df

    def _handle_drift(
        self,
        name: str,
        old: SchemaSnapshot,
        new: SchemaSnapshot,
        events: list,
        on_drift: str,
    ) -> None:
        """Handle detected drift based on configuration.

        Args:
            name: Schema name
            old: Previous snapshot
            new: Current snapshot
            events: List of drift events
            on_drift: Action ("warn", "raise", "log", "alert")
        """
        if on_drift == "raise":
            raise SchemaDriftError(
                f"Schema drift detected in '{name}': {len(events)} events (v{old.version} → v{new.version})"
            )
        elif on_drift == "alert" and self.alerter:
            self.alerter.alert(name, old, new, events)
        elif on_drift == "warn":
            self._warn(name, old, new, events)
        elif on_drift == "log":
            self._log(name, old, new, events)

    def _warn(self, name: str, old: SchemaSnapshot, new: SchemaSnapshot, events: list) -> None:
        """Print warning to terminal."""
        if self.alerter:
            self.alerter.alert(name, old, new, events)

    def _log(self, name: str, old: SchemaSnapshot, new: SchemaSnapshot, events: list) -> None:
        """Log to file (TODO: implement proper logging)."""
        import logging

        logger = logging.getLogger("sentinel")
        logger.warning(
            f"Schema drift in '{name}': {len(events)} events (v{old.version} → v{new.version})"
        )

    def compare(self, name: str):
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
        return _CompareContext(self, name)

    def diff(self, name: str, version1: int, version2: int) -> list:
        """Compare two versions of a schema.

        Args:
            name: Schema name
            version1: First version number
            version2: Second version number

        Returns:
            List of DriftEvents between versions
        """
        snap1 = self.store.load_version(name, version1)
        snap2 = self.store.load_version(name, version2)

        if not snap1 or not snap2:
            raise ValueError(f"Version not found for schema '{name}'")

        return detect_drift(snap1, snap2, rules=self.config.enabled_rules)

    def history(self, name: str, last_n: int = 10) -> list[SchemaSnapshot]:
        """Get recent schema history.

        Args:
            name: Schema name
            last_n: Number of recent versions to return

        Returns:
            List of SchemaSnapshots, newest first
        """
        return self.store.history(name, last_n)

    def list_schemas(self) -> list[str]:
        """List all tracked schemas.

        Returns:
            List of schema names
        """
        return self.store.list_schemas()


class _CompareContext:
    """Context manager for explicit schema comparison."""

    def __init__(self, sentinel: Sentinel, name: str):
        self.sentinel = sentinel
        self.name = name
        self.snapshot = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def check(self, df: Any, on_drift: str = "warn", profiler_type: str = "pandas") -> None:
        """Check a DataFrame for schema drift.

        Args:
            df: DataFrame to check
            on_drift: Action on detected drift
            profiler_type: Type of profiler to use
        """
        self.sentinel.wrap(df, name=self.name, on_drift=on_drift, profiler_type=profiler_type)
