"""
Example 1: Basic decorator usage

This example shows how to use the @sentinel.watch decorator to automatically
track schema changes in a data loading function.
"""

import pandas as pd
import sentinel


@sentinel.watch("orders_df", on_drift="warn")
def load_orders(filename: str) -> pd.DataFrame:
    """Load orders from CSV and track schema."""
    df = pd.read_csv(filename)
    print(f"✓ Loaded {len(df)} orders from {filename}")
    return df


if __name__ == "__main__":
    # First run: baseline is created
    print("\n--- First run (baseline) ---")
    df1 = load_orders("orders_v1.csv")

    # Second run: drift is detected against baseline
    print("\n--- Second run (checking against baseline) ---")
    df2 = load_orders("orders_v2.csv")

    print("\n✓ Done")
