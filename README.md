# DataSchema Sentinel

[![Tests](https://github.com/tanuj437/dataschema-sentinel/workflows/Tests/badge.svg)](https://github.com/tanuj437/dataschema-sentinel/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

Zero-config schema drift detection for data pipelines. Catch breaking schema changes before they break your data workflows.

**Why:** Silent schema changes break downstream pipelines. This tool detects them automatically with zero setup.

## What is schema drift?

Silent, incremental changes to your data:
- A column that was never null starts allowing nulls
- `float64` silently becomes `object` because someone uploaded a CSV with a stray string "N/A"
- A table gains 3 columns nobody documented
- Row counts fluctuate wildly without explanation

These changes break downstream pipelines, wake you up at 3am, and are nearly impossible to trace without proper monitoring.

## Why Sentinel?

- **Zero-config first run** — no schema files to maintain, just wrap your DataFrame
- **Versioned snapshots** — compare any two historical states
- **CI-ready** — `on_drift="raise"` throws an exception; perfect for preventing bad data from reaching prod
- **Human-readable diffs** — see exactly what changed and why it matters
- **Lightweight** — no heavy orchestration, no database server

## Quick start

### Installation

```bash
# From PyPI (coming soon)
# pip install dataschema-sentinel

# From GitHub
git clone https://github.com/tanuj437/dataschema-sentinel.git
cd dataschema-sentinel
pip install -e .

# With all optional dependencies
pip install -e ".[all]"
```

### Using the decorator

```python
import pandas as pd
import sentinel

@sentinel.watch("orders_df", on_drift="raise")
def load_orders(date: str) -> pd.DataFrame:
    return pd.read_csv(f"orders_{date}.csv")

# First run: profiles schema, saves baseline
df = load_orders("2025-01-01")

# Second run: compares against baseline
df = load_orders("2025-01-02")
#  ✗ SchemaDriftError: Schema drift detected in 'orders_df'
#    Column 'amount' type changed: float64 → object
```

### Inline wrapping

```python
df = pd.read_csv("data.csv")
df = sentinel.wrap(df, name="my_data", on_drift="warn")
```

### Explicit comparison

```python
with sentinel.compare("public.users") as ctx:
    df = pd.read_sql("SELECT * FROM users", engine)
    ctx.check(df)
```

## `on_drift` modes

- `"raise"` — Throw `SchemaDriftError` (best for CI/CD pipelines)
- `"warn"` — Print colored table to terminal (default for interactive work)
- `"log"` — Write to Python logger (silent in production)
- `"alert"` — Send to Slack/email (coming soon)

## Example: catching a real-world drift

Your production CSV suddenly contains a typo in a header:

```python
# In the data, 'amount' is now "n/a" for a few rows
df = pd.read_csv("orders.csv")
df = sentinel.wrap(df, name="orders", on_drift="raise")

# Output:
# ╔═══════════════════════════════════════════════════════════╗
# ║ Schema drift detected: orders  v1 → v2                    ║
# ╠════════════╦════════════╦══════════════╦═══════════════════╣
# ║ Severity   ║ Column     ║ Rule         ║ Change            ║
# ╠════════════╬════════════╬══════════════╬═══════════════════╣
# ║ BREAKING   ║ amount     ║ TYPE_CHANGED ║ float64 → object  ║
# ║ WARNING    ║ (table)    ║ ROW_COUNT... ║ increased by 2%   ║
# ╚════════════╩════════════╩══════════════╩═══════════════════╝
#   [bold red]1 BREAKING[/] · [yellow]1 WARNING[/]
```

Your CI pipeline fails before bad data reaches the warehouse. Problem solved.

## Detection rules

Sentinel detects six categories of drift:

| Rule | Severity | What it catches |
|------|----------|-----------------|
| `COLUMN_DROPPED` | BREAKING | A column disappeared |
| `COLUMN_ADDED` | WARNING | A new column appeared |
| `TYPE_CHANGED` | BREAKING | Column dtype changed (unless safe widening) |
| `NULLABILITY_CHANGED` | WARNING | Null policy changed for a column |
| `STATS_DRIFTED` | INFO | Numeric column mean shifted >20% |
| `ROW_COUNT_CHANGED` | WARNING | Row count changed >10% |

## CLI

```bash
# Show schema history
sentinel history orders_df --last 20

# Compare two versions
sentinel diff orders_df --version 3 --version 7

# List all tracked schemas
sentinel list

# Export snapshot as JSON
sentinel export orders_df --version 5 --format json
```

## Custom detection rules

Define domain-specific drift rules:

```python
from sentinel import rule

@rule("transaction_amount_never_null", severity="BREAKING")
def check_amount_nulls(snapshot):
    col = snapshot.columns.get("transaction_amount")
    if col and col.null_pct > 0:
        return f"transaction_amount has {col.null_pct}% nulls — never acceptable"
    return None
```

## Supported data sources

- **pandas** — ✓ Fully implemented
- **Polars** — ◐ Skeleton ready (implement in `profiler/polars_profiler.py`)
- **SQL (via SQLAlchemy)** — ◐ Skeleton ready (implement in `profiler/sql_profiler.py`)

## Configuration

```python
from sentinel import configure, SentinelConfig

config = SentinelConfig(
    db_path="~/.sentinel/schemas.db",           # Where to store snapshots
    row_count_threshold=0.1,                    # Trigger at 10% row count change
    stats_drift_threshold=0.2,                  # Trigger at 20% mean shift
    enabled_rules=["column_dropped", "type_changed"],  # Which rules to run
)

configure(config)
```

## Architecture

```
sentinel/
├── core.py              # Main Sentinel class
├── profiler/            # Schema extraction (pandas, Polars, SQL)
├── detector/            # Drift detection logic
├── store/               # Versioned snapshot storage (SQLite)
├── diff/                # Diff generation
└── alerts/              # Notifications (terminal, Slack, JSON)
```

## Testing

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run all tests (23 test cases)
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=sentinel --cov-report=html
```

## Development status

- ✓ Core architecture, pandas profiler, drift detection
- ◐ SQL/Polars profilers (need implementation)
- ◐ Slack alerter (need implementation)
- 🔜 Custom rule evaluation
- 🔜 Async profiling for large tables
- 🔜 Drift prediction (statistical forecasting)

## License

MIT

## Contributing

Contributions welcome! Start with the skeleton implementations in `profiler/` or `alerts/` and add test coverage.

## Feedback

Found a bug? Have a feature idea? Open an issue on [GitHub](https://github.com/tanuj437/dataschema-sentinel/issues).
