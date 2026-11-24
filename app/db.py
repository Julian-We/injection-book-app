import os
import re
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
    _migrate_experiments_unique_slug(conn)


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


def _has_unique_index_on(conn: sqlite3.Connection, table: str, columns: list[str]) -> bool:
    # index_list rows: (seq, name, unique, origin, partial); index_info rows: (seqno, cid, name)
    for idx in conn.execute(f"PRAGMA index_list({table})").fetchall():
        if not idx[2]:
            continue
        cols = [r[2] for r in conn.execute(f"PRAGMA index_info('{idx[1]}')").fetchall()]
        if cols == columns:
            return True
    return False


def _migrate_experiments_unique_slug(conn: sqlite3.Connection) -> None:
    """One-time migration: older databases have `slug TEXT NOT NULL UNIQUE`. Replace it
    with UNIQUE(slug, experiment_date) so a title can be reused on another date.

    SQLite can't drop a constraint, so the table is rebuilt (the standard
    create-copy-drop-rename procedure). Foreign keys must be OFF while doing so -
    otherwise dropping the old table would cascade-delete every mix. IDs are kept,
    so mixes stay attached to their experiments.
    """
    if not _has_unique_index_on(conn, "experiments", ["slug"]):
        return
    create_sql = re.search(
        r"CREATE TABLE IF NOT EXISTS experiments \((.*?)\n\);", SCHEMA_PATH.read_text(), re.S
    ).group(1)
    # table_info rows: (cid, name, type, notnull, dflt_value, pk)
    old_cols = [r[1] for r in conn.execute("PRAGMA table_info(experiments)").fetchall()]
    conn.commit()
    conn.execute("PRAGMA foreign_keys = OFF")
    try:
        conn.execute("BEGIN")
        conn.execute(f"CREATE TABLE experiments_new ({create_sql}\n)")
        new_cols = [r[1] for r in conn.execute("PRAGMA table_info(experiments_new)").fetchall()]
        cols = ", ".join(c for c in old_cols if c in new_cols)
        conn.execute(f"INSERT INTO experiments_new ({cols}) SELECT {cols} FROM experiments")
        conn.execute("DROP TABLE experiments")
        conn.execute("ALTER TABLE experiments_new RENAME TO experiments")
        problems = conn.execute("PRAGMA foreign_key_check").fetchall()
        if problems:
            raise RuntimeError(f"foreign key check failed after rebuilding experiments: {problems[:5]}")
        conn.commit()
        print("Migrated experiments table: titles now only need to be unique per date.")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.execute("PRAGMA foreign_keys = ON")


def table_count(conn: sqlite3.Connection, table: str) -> int:
    return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]


def get_db():
    """FastAPI dependency: one connection per request."""
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()
