"""
Example 4: Custom drift rules

This example shows how to define custom domain-specific drift detection rules.
"""

import pandas as pd
import sentinel
from sentinel import rule


# Define custom rules for our business logic
@rule("payment_amount_never_null", severity="BREAKING")
def check_payment_amount(snapshot):
    """Payment amount must never be null."""
    col = snapshot.columns.get("amount")
    if col and col.null_pct > 0:
        return f"CRITICAL: payment amount has {col.null_pct}% nulls!"
    return None


@rule("customer_count_warning", severity="WARNING")
def check_customer_count(snapshot):
    """Warn if table is getting too large."""
    if snapshot.row_count > 1_000_000:
        return f"Table growing large: {snapshot.row_count:,} rows"
    return None


if __name__ == "__main__":
    print("Loading payment data with custom rules...")

    df = pd.DataFrame({
        "id": [1, 2, 3, 4, 5],
        "customer_id": [100, 101, 102, 103, 104],
        "amount": [49.99, 99.99, 29.99, 199.99, 14.99],
    })

    # Wrap with monitoring
    df = sentinel.wrap(df, name="payments", on_drift="raise")

    print(f"✓ Monitored {len(df)} payments")
    print("✓ Custom rules registered and active")
