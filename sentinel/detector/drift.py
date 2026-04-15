from __future__ import annotations

"""Core drift detection logic."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from sentinel.store.models import SchemaSnapshot

class DriftSeverity(Enum):
    """Severity levels for drift events."""

    BREAKING = "BREAKING"  # Pipeline will fail
    WARNING = "WARNING"  # Unexpected but may be okay
    INFO = "INFO"  # Interesting but low risk

@dataclass
class DriftEvent:
    """A single drift event."""

    column: Optional[str]  # None for table-level events
    rule: str  # "COLUMN_DROPPED", "TYPE_CHANGED", etc.
    severity: DriftSeverity
    message: str
    old_value: Optional[str]
    new_value: Optional[str]

def detect_drift(
    old: SchemaSnapshot,
    new: SchemaSnapshot,
    rules: list[str] | None = None,
    row_count_threshold: float = 0.1,
    stats_drift_threshold: float = 0.2,
) -> list[DriftEvent]:
    """Compare two snapshots and return all drift events.

    Args:
        old: Previous SchemaSnapshot
        new: Current SchemaSnapshot
        rules: List of rules to apply (None = all)
        row_count_threshold: Fractional change threshold for row count
        stats_drift_threshold: Fractional change threshold for numeric stats

    Returns:
        List of DriftEvent, sorted by severity
    """
    all_rules = rules or [
        "column_dropped",
        "column_added",
        "type_changed",
        "nullability_changed",
        "stats_drifted",
        "row_count_changed",
    ]
    events = []

    if "column_dropped" in all_rules:
        events.extend(_check_dropped_columns(old, new))
    if "column_added" in all_rules:
        events.extend(_check_added_columns(old, new))
    if "type_changed" in all_rules:
        events.extend(_check_type_changes(old, new))
    if "nullability_changed" in all_rules:
        events.extend(_check_nullability(old, new))
    if "stats_drifted" in all_rules:
        events.extend(_check_stats_drift(old, new, stats_drift_threshold))
    if "row_count_changed" in all_rules:
        events.extend(_check_row_count(old, new, row_count_threshold))

    # Sort by severity
    severity_order = {DriftSeverity.BREAKING: 0, DriftSeverity.WARNING: 1, DriftSeverity.INFO: 2}
    return sorted(events, key=lambda e: severity_order[e.severity])

def _check_dropped_columns(old: SchemaSnapshot, new: SchemaSnapshot) -> list[DriftEvent]:
    """Check for dropped columns."""
    dropped = set(old.columns) - set(new.columns)
    return [
        DriftEvent(
            column=col,
            rule="COLUMN_DROPPED",
            severity=DriftSeverity.BREAKING,
            message=f"Column '{col}' ({old.columns[col].dtype}) was dropped",
            old_value=old.columns[col].dtype,
            new_value=None,
        )
        for col in dropped
    ]

def _check_added_columns(old: SchemaSnapshot, new: SchemaSnapshot) -> list[DriftEvent]:
    """Check for added columns."""
    added = set(new.columns) - set(old.columns)
    return [
        DriftEvent(
            column=col,
            rule="COLUMN_ADDED",
            severity=DriftSeverity.WARNING,
            message=f"New column '{col}' ({new.columns[col].dtype}) appeared",
            old_value=None,
            new_value=new.columns[col].dtype,
        )
        for col in added
    ]

def _check_type_changes(old: SchemaSnapshot, new: SchemaSnapshot) -> list[DriftEvent]:
    """Check for type changes."""
    events = []
    for col in set(old.columns) & set(new.columns):
        old_type = old.columns[col].dtype
        new_type = new.columns[col].dtype
        if old_type != new_type:
            severity = DriftSeverity.BREAKING
            if _is_safe_widening(old_type, new_type):
                severity = DriftSeverity.WARNING
            events.append(
                DriftEvent(
                    column=col,
                    rule="TYPE_CHANGED",
                    severity=severity,
                    message=f"Column '{col}' type changed: {old_type} → {new_type}",
                    old_value=old_type,
                    new_value=new_type,
                )
            )
    return events

def _check_nullability(old: SchemaSnapshot, new: SchemaSnapshot) -> list[DriftEvent]:
    """Check for nullability changes."""
    events = []
    for col in set(old.columns) & set(new.columns):
        old_null = old.columns[col].nullable
        new_null = new.columns[col].nullable
        if old_null != new_null:
            severity = DriftSeverity.WARNING if new_null else DriftSeverity.INFO
            direction = "now has nulls" if new_null else "no longer has nulls"
            events.append(
                DriftEvent(
                    column=col,
                    rule="NULLABILITY_CHANGED",
                    severity=severity,
                    message=f"Column '{col}' {direction} (null%: {old.columns[col].null_pct}% → {new.columns[col].null_pct}%)",
                    old_value=str(old_null),
                    new_value=str(new_null),
                )
            )
    return events

def _check_stats_drift(
    old: SchemaSnapshot, new: SchemaSnapshot, threshold: float = 0.2
) -> list[DriftEvent]:
    """Check for statistical drift in numeric columns."""
    events = []
    for col in set(old.columns) & set(new.columns):
        o = old.columns[col]
        n = new.columns[col]
        if o.mean_val is None or n.mean_val is None:
            continue
        if o.mean_val == 0:
            continue
        shift = abs(n.mean_val - o.mean_val) / abs(o.mean_val)
        if shift > threshold:
            events.append(
                DriftEvent(
                    column=col,
                    rule="STATS_DRIFTED",
                    severity=DriftSeverity.INFO,
                    message=f"Column '{col}' mean shifted {shift*100:.1f}%: {o.mean_val:.3g} → {n.mean_val:.3g}",
                    old_value=str(round(o.mean_val, 4)),
                    new_value=str(round(n.mean_val, 4)),
                )
            )
    return events

def _check_row_count(
    old: SchemaSnapshot, new: SchemaSnapshot, threshold: float = 0.1
) -> list[DriftEvent]:
    """Check for significant row count changes."""
    if old.row_count == 0:
        return []
    change = (new.row_count - old.row_count) / old.row_count
    if abs(change) > threshold:
        direction = "increased" if change > 0 else "decreased"
        return [
            DriftEvent(
                column=None,
                rule="ROW_COUNT_CHANGED",
                severity=DriftSeverity.WARNING,
                message=f"Row count {direction} by {abs(change)*100:.1f}%: {old.row_count:,} → {new.row_count:,}",
                old_value=str(old.row_count),
                new_value=str(new.row_count),
            )
        ]
    return []

def _is_safe_widening(old_type: str, new_type: str) -> bool:
    """Check if type change is a safe widening (int32→int64, float32→float64)."""
    safe_widenings = {
        ("int32", "int64"),
        ("int16", "int64"),
        ("int8", "int64"),
        ("float32", "float64"),
    }
    return (old_type, new_type) in safe_widenings
