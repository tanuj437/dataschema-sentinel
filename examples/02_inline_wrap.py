"""
Example 2: Inline wrapping

This example shows how to use sentinel.wrap() to track schema changes
for DataFrames you don't own or can't modify directly.
"""

import pandas as pd
import sentinel


def load_and_clean_data(filename: str) -> pd.DataFrame:
    """Load and clean data (not owned by us)."""
    df = pd.read_csv(filename)
    df["date"] = pd.to_datetime(df["date"])
    df = df.drop_duplicates()
    return df


if __name__ == "__main__":
    # Load data and wrap it for monitoring
    print("Loading data...")
    df = load_and_clean_data("customers.csv")

    # Wrap with sentinel to track schema
    df = sentinel.wrap(df, name="customers", on_drift="raise")

    print(f"✓ Loaded and monitored {len(df)} customer records")
    print("✓ Schema baseline saved")
