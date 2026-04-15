"""Structured JSON alerter."""

import json
from pathlib import Path
from typing import Optional

from sentinel.alerts.base import BaseAlerter
from sentinel.detector.drift import DriftEvent
from sentinel.diff.engine import DiffEngine
from sentinel.store.models import SchemaSnapshot


class JSONAlerter(BaseAlerter):
    """Alert via structured JSON output."""

    def __init__(self, output_path: Path | str | None = None):
        """Initialize JSON alerter.

        Args:
            output_path: Path to write JSON alerts (default: stdout if None)
        """
        self.output_path = Path(output_path) if output_path else None

    def alert(
        self,
        name: str,
        old_snapshot: SchemaSnapshot,
        new_snapshot: SchemaSnapshot,
        events: list[DriftEvent],
    ) -> None:
        """Write drift alert as JSON.

        Args:
            name: Schema name
            old_snapshot: Previous snapshot
            new_snapshot: Current snapshot
            events: List of drift events
        """
        alert_data = {
            "schema_name": name,
            "old_version": old_snapshot.version,
            "new_version": new_snapshot.version,
            "old_row_count": old_snapshot.row_count,
            "new_row_count": new_snapshot.row_count,
            "events": [DiffEngine.format_event(e) for e in events],
            "summary": DiffEngine.summary(events),
        }

        json_str = json.dumps(alert_data, indent=2)

        if self.output_path:
            self.output_path.write_text(json_str)
        else:
            print(json_str)
