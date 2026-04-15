"""Built-in and custom drift detection rules."""

from __future__ import annotations

from typing import Callable, Optional

from sentinel.detector.drift import DriftEvent, DriftSeverity
from sentinel.store.models import SchemaSnapshot


# Registry of custom rules
_custom_rules: dict[str, Callable] = {}


def rule(name: str, severity: str = "WARNING") -> Callable:
    """Decorator to register a custom drift detection rule.

    Args:
        name: Name of the rule (e.g., "transaction_amount_never_null")
        severity: Default severity ("BREAKING", "WARNING", or "INFO")

    Returns:
        Decorator function

    Example:
        @rule("amount_never_null", severity="BREAKING")
        def check_amount_nulls(snapshot: SchemaSnapshot) -> Optional[str]:
            col = snapshot.columns.get("transaction_amount")
            if col and col.null_pct > 0:
                return f"transaction_amount has {col.null_pct}% nulls"
            return None
    """

    def decorator(func: Callable) -> Callable:
        _custom_rules[name] = (func, severity)
        return func

    return decorator


def get_custom_rules() -> dict[str, tuple[Callable, str]]:
    """Get all registered custom rules."""
    return _custom_rules.copy()
