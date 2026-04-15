# Quick Start Guide

## 1-minute setup

```bash
# Clone the repo
git clone https://github.com/tanuj437/dataschema-sentinel.git
cd dataschema-sentinel

# Install
pip install -e .

# Run tests
pip install -e ".[dev]"
pytest tests/
```

## 30-second usage example

```python
import pandas as pd
import sentinel

# Wrap any DataFrame to track schema
@sentinel.watch("my_data", on_drift="raise")
def load_data():
    return pd.read_csv("data.csv")

df = load_data()  # First run: baseline saved
df = load_data()  # Second run: drift detected automatically
```

## What gets detected

| Change | Severity | Example |
|--------|----------|---------|
| Column dropped | 🔴 BREAKING | `amount` column disappears |
| Type changed | 🔴 BREAKING | `price` becomes `object` (was `float64`) |
| New column | 🟡 WARNING | New column `status` appears |
| Nullability changed | 🟡 WARNING | `user_id` now has nulls (was never null) |
| Stats drift | 🟢 INFO | Average price shifted >20% |
| Row count changed | 🟡 WARNING | Table size changed >10% |

## Commands

```bash
# Show schema history
sentinel history my_data --last 20

# Compare two versions
sentinel diff my_data --version 3 --version 7

# Export schema as JSON
sentinel export my_data --version 5 --format json

# List all tracked schemas
sentinel list
```

## Configuration

```python
from sentinel import configure, SentinelConfig

config = SentinelConfig(
    row_count_threshold=0.1,      # 10% row count change
    stats_drift_threshold=0.2,    # 20% mean shift
)
configure(config)
```

## Next steps

- Read [README.md](README.md) for full API documentation
- See [examples/](examples/) directory for more patterns
- Check [CONTRIBUTING.md](CONTRIBUTING.md) to contribute
