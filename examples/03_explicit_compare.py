"""
Example 3: Explicit comparison

This example shows how to use the context manager pattern for more
explicit control over schema comparison.
"""

import pandas as pd
import sqlalchemy as sa
import sentinel


if __name__ == "__main__":
    # For this example, we'll use a CSV instead of a real database
    # In production, you'd use: engine = sa.create_engine("postgresql://...")

    print("Loading transaction data...")

    # Load from CSV
    df = pd.read_csv("transactions.csv")

    # Use context manager for explicit comparison
    with sentinel.compare("transactions") as ctx:
        ctx.check(df, on_drift="warn")

    print(f"✓ Checked {len(df)} transactions")
    print("✓ Schema comparison complete")
