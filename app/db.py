import os
import sqlite3
from pathlib import Path
from contextlib import contextmanager

DB_PATH = os.environ.get("DATABASE_PATH", "/data/injection.db")
SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def get_connection() -> sqlite3.Connection:
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def connection():
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def ensure_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA_PATH.read_text())
    conn.commit()
    _migrate_add_column(conn, "experiments", "closed_at", "TEXT")
    _migrate_add_column(conn, "mixes", "phr_volume", "REAL")


def _migrate_add_column(conn: sqlite3.Connection, table: str, column: str, coltype: str) -> None:
    """Idempotent lightweight migration: add a column if it doesn't exist yet.

    CREATE TABLE IF NOT EXISTS (in schema.sql) never alters an already-existing
    table, so new columns added after the app was first deployed need this.
    """
    try:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {coltype}")
        conn.commit()
    except sqlite3.OperationalError as e:
        if "duplicate column name" not in str(e):
            raise


def table_count(conn: sqlite3.Connection, table: str) -> int:
    return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]


def get_db():
    """FastAPI dependency: one connection per request."""
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()
