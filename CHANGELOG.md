# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-04-15

### Added
- Core Sentinel class for schema drift detection
- **Profilers:** Full pandas implementation; Polars and SQL profilers (skeleton)
- **Drift Detection:** 6 built-in rules (column_dropped, column_added, type_changed, nullability_changed, stats_drifted, row_count_changed)
- **Storage:** SQLite-backed versioned schema snapshots with auto-increment versioning
- **Alerters:** Rich terminal output with colored tables; JSON structured output; Slack webhook (skeleton)
- **CLI:** Commands for `diff`, `history`, `list`, `export`
- **Decorators:** `@sentinel.watch()` for automatic schema tracking
- **Context managers:** `with sentinel.compare()` for explicit comparisons
- **Configuration:** `SentinelConfig` for customization of detection rules and thresholds
- **Tests:** 23 comprehensive test cases across all modules (23/23 passing)
- **Examples:** 4 example scripts demonstrating each usage pattern
- **Documentation:** Full README with usage guides, API reference, and architecture overview
- **Contributing guide:** Clear path for implementing remaining profilers and alerters

### In Progress
- Polars DataFrame profiler
- SQL table profiler (via SQLAlchemy information_schema)
- Slack webhook alerter
- Custom rule evaluation integration

### Planned
- Async profiling for large tables
- Drift prediction with statistical forecasting
- Web dashboard for schema history visualization
- Email alerter
- Cloud storage backends (S3, GCS)
- Schema registry integration (Confluent)

---

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on contributing features, profilers, and alerters.
