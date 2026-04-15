# Contributing to DataSchema Sentinel

Thanks for your interest in contributing! This guide will help you get started.

## Development setup

```bash
git clone https://github.com/tanuj437/dataschema-sentinel.git
cd dataschema-sentinel
pip install -e ".[dev]"
```

## Running tests

```bash
# Run all tests
pytest tests/ -v

# Run a specific test file
pytest tests/test_profiler.py -v

# Run with coverage
pytest tests/ --cov=sentinel --cov-report=html
```

All tests must pass before submitting a PR. Current status: **23/23 passing** ✓

## Project structure

- **`sentinel/core.py`** — Main Sentinel class (entry point)
- **`sentinel/profiler/`** — Data source profilers (pandas ✓, polars ◐, sql ◐)
- **`sentinel/detector/`** — Drift detection logic (6 rules)
- **`sentinel/store/`** — Versioned schema storage (SQLite)
- **`sentinel/alerts/`** — Alerters (terminal ✓, json ✓, slack ◐)
- **`sentinel/diff/`** — Diff generation and severity scoring
- **`sentinel/cli.py`** — Command-line interface

## High-priority areas for contribution

### 1. Polars profiler (`sentinel/profiler/polars_profiler.py`)

Implement schema profiling for Polars DataFrames. Reference: `sentinel/profiler/pandas_profiler.py`

```python
def profile(self, df: polars.DataFrame, name: str, version: int) -> SchemaSnapshot:
    # Extract dtype, nullability, stats from Polars DataFrame
    # Return SchemaSnapshot
    pass
```

**Tests:** `tests/test_profiler.py::TestPolarsProfiler` (skeleton ready)

### 2. SQL profiler (`sentinel/profiler/sql_profiler.py`)

Implement schema profiling for SQL tables via SQLAlchemy without loading full data.

```python
def profile(self, engine, table_name: str, name: str, version: int) -> SchemaSnapshot:
    # Use information_schema to extract metadata
    # Calculate stats via SQL queries
    # Return SchemaSnapshot
    pass
```

**Tip:** Use `SELECT COUNT(*), COUNT(col) FROM table` for null counts, avoiding full scans.

### 3. Slack alerter (`sentinel/alerts/slack.py`)

Implement Slack webhook alerts for drift events.

```python
def alert(self, name: str, old: SchemaSnapshot, new: SchemaSnapshot, events: list[DriftEvent]):
    # Format events as Slack message
    # POST to webhook_url
    pass
```

**Dependency:** `slack-sdk>=3.21.0` (already in `pyproject.toml[slack]`)

### 4. Custom rule evaluation

Extend `sentinel/detector/drift.py` to evaluate registered custom rules during detection.

## Code style

- Follow PEP 8
- Use type hints
- Add docstrings to public functions
- Keep lines under 100 characters

```bash
# Format code
black sentinel/

# Lint
ruff check sentinel/
```

## Adding tests

Every new feature should have test coverage. Place tests in `tests/` matching the module name.

Example test structure:

```python
def test_my_feature(sentinel, sample_dataframe):
    """Test description."""
    result = sentinel.my_feature(sample_dataframe)
    assert result.something_expected
```

Run tests after changes:
```bash
pytest tests/ -v
```

## Submitting a PR

1. **Fork** the repo
2. **Create branch:** `git checkout -b feature/your-feature`
3. **Make changes** with test coverage
4. **Run tests:** `pytest tests/ -v`
5. **Commit:** `git commit -m "Add your feature"`
6. **Push:** `git push origin feature/your-feature`
7. **Open PR** on GitHub

## Roadmap

- ✓ Core architecture, pandas profiler, drift detector, tests
- ◐ SQL/Polars profilers (help needed!)
- ◐ Slack alerter (help needed!)
- 🔜 Custom rule execution in detector
- 🔜 Async profiling for large tables
- 🔜 Drift prediction (statistical forecasting)
- 🔜 Web dashboard for schema history

## Questions?

Open an issue on [GitHub](https://github.com/tanuj437/dataschema-sentinel/issues) — we're happy to help!
