"""Configuration for Sentinel."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal


@dataclass
class SentinelConfig:
    """Configuration for Sentinel behavior."""

    db_path: Path = field(default_factory=lambda: Path.home() / ".sentinel" / "schemas.db")
    enabled_rules: list[str] = field(
        default_factory=lambda: [
            "column_dropped",
            "column_added",
            "type_changed",
            "nullability_changed",
            "stats_drifted",
            "row_count_changed",
        ]
    )
    row_count_threshold: float = 0.1  # 10% change triggers ROW_COUNT_CHANGED
    stats_drift_threshold: float = 0.2  # 20% mean shift triggers STATS_DRIFTED
    on_drift: Literal["warn", "raise", "log", "alert"] = "warn"
    verbose: bool = False

    def __post_init__(self):
        """Ensure db_path parent directory exists."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
