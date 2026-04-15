"""SQLite-backed versioned schema storage."""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

from sentinel.store.models import ColumnProfile, SchemaSnapshot


class SchemaStore:
    """Versioned schema storage backed by SQLite."""

    def __init__(self, db_path: Path | None = None):
        """Initialize the schema store.

        Args:
            db_path: Path to SQLite database (default: ~/.sentinel/schemas.db)
        """
        self.db_path = db_path or (Path.home() / ".sentinel" / "schemas.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS snapshots (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    name        TEXT NOT NULL,
                    version     INTEGER NOT NULL,
                    captured_at TEXT NOT NULL,
                    row_count   INTEGER NOT NULL,
                    source_type TEXT NOT NULL,
                    columns_json TEXT NOT NULL,
                    tags_json   TEXT DEFAULT '{}'
                )
            """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_name ON snapshots(name)")
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_name_version ON snapshots(name, version)"
            )

    def save(self, snapshot: SchemaSnapshot) -> int:
        """Save snapshot, auto-incrementing version.

        Args:
            snapshot: SchemaSnapshot to save

        Returns:
            New version number
        """
        version = self._next_version(snapshot.name)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO snapshots (name, version, captured_at, row_count, source_type, columns_json, tags_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    snapshot.name,
                    version,
                    snapshot.captured_at.isoformat(),
                    snapshot.row_count,
                    snapshot.source_type,
                    json.dumps({k: vars(v) for k, v in snapshot.columns.items()}),
                    json.dumps(snapshot.tags),
                ),
            )
        return version

    def load_latest(self, name: str) -> Optional[SchemaSnapshot]:
        """Load the most recent snapshot for a given name.

        Args:
            name: Schema name

        Returns:
            Latest SchemaSnapshot or None
        """
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                """
                SELECT * FROM snapshots WHERE name = ?
                ORDER BY version DESC LIMIT 1
            """,
                (name,),
            ).fetchone()
        return self._row_to_snapshot(row) if row else None

    def load_version(self, name: str, version: int) -> Optional[SchemaSnapshot]:
        """Load a specific version of a snapshot.

        Args:
            name: Schema name
            version: Version number

        Returns:
            SchemaSnapshot or None
        """
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT * FROM snapshots WHERE name = ? AND version = ?", (name, version)
            ).fetchone()
        return self._row_to_snapshot(row) if row else None

    def history(self, name: str, last_n: int = 10) -> list[SchemaSnapshot]:
        """Load recent snapshot history.

        Args:
            name: Schema name
            last_n: Number of recent snapshots to return

        Returns:
            List of SchemaSnapshots, newest first
        """
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                """
                SELECT * FROM snapshots WHERE name = ?
                ORDER BY version DESC LIMIT ?
            """,
                (name, last_n),
            ).fetchall()
        return [self._row_to_snapshot(r) for r in rows if r]

    def list_schemas(self) -> list[str]:
        """List all tracked schema names.

        Returns:
            List of schema names
        """
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("SELECT DISTINCT name FROM snapshots ORDER BY name").fetchall()
        return [row[0] for row in rows]

    def _next_version(self, name: str) -> int:
        """Get next version number for a schema name."""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("SELECT MAX(version) FROM snapshots WHERE name = ?", (name,)).fetchone()
        return (row[0] or 0) + 1

    @staticmethod
    def _row_to_snapshot(row: tuple) -> Optional[SchemaSnapshot]:
        """Convert database row to SchemaSnapshot."""
        if not row:
            return None
        _, name, version, captured_at, row_count, source_type, columns_json, tags_json = row
        raw_cols = json.loads(columns_json)
        columns = {k: ColumnProfile(**v) for k, v in raw_cols.items()}
        return SchemaSnapshot(
            name=name,
            captured_at=datetime.fromisoformat(captured_at),
            row_count=row_count,
            columns=columns,
            source_type=source_type,
            version=version,
            tags=json.loads(tags_json),
        )
