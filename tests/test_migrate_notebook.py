import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db import ensure_schema  # noqa: E402
from migrations import migrate_plasmids, migrate_notebook  # noqa: E402


@pytest.fixture
def conn():
    c = sqlite3.connect(":memory:")
    c.row_factory = sqlite3.Row
    ensure_schema(c)
    migrate_plasmids.run(c)
    yield c
    c.close()


def test_imports_all_experiments_mixes_and_lines(conn):
    result = migrate_notebook.run(conn)
    assert result["experiments"] == 41
    assert result["mixes"] == 81
    assert result["lines"] == 271
    assert result["flagged"] == 6


def test_preview_only_vs_written_experiment_counts(conn):
    migrate_notebook.run(conn)
    counts = dict(conn.execute(
        "SELECT source, COUNT(*) c FROM experiments GROUP BY source"
    ).fetchall())
    assert counts["migrated_notebook_written"] == 24
    assert counts["migrated_notebook_preview_only"] == 17


def test_b465_inject_volume_override_preserved(conn):
    migrate_notebook.run(conn)
    rows = conn.execute(
        """SELECT ml.inject_volume, ml.needs_review FROM mix_lines ml
           JOIN mixes m ON ml.mix_id = m.id
           WHERE m.label IN ('oct13a', 'oct13b', 'oct13c')
             AND ml.display_name_override LIKE '%B465%'"""
    ).fetchall()
    assert len(rows) == 3
    assert all(r["inject_volume"] == 6 for r in rows)
    assert all(r["needs_review"] == 1 for r in rows)


def test_f458_name_mismatch_flagged_in_all_three_occurrences(conn):
    migrate_notebook.run(conn)
    rows = conn.execute(
        "SELECT needs_review FROM mix_lines WHERE display_name_override LIKE '%F458%'"
    ).fetchall()
    assert len(rows) == 3
    assert all(r["needs_review"] == 1 for r in rows)


def test_cell30_split_into_two_experiments_same_date(conn):
    migrate_notebook.run(conn)
    rows = conn.execute(
        "SELECT slug, experiment_date FROM experiments WHERE source_label = 'arch24'"
    ).fetchall()
    assert len(rows) == 2
    assert {r["experiment_date"] for r in rows} == {"2026-03-24"}


def test_raises_if_a_construct_id_is_missing_from_plasmids():
    c = sqlite3.connect(":memory:")
    c.row_factory = sqlite3.Row
    ensure_schema(c)
    # Deliberately skip migrate_plasmids - every notebook construct ID should be
    # unresolvable, so the notebook migration must fail loudly, not silently.
    with pytest.raises(AssertionError):
        migrate_notebook.run(c)
    c.close()


def test_idempotent_on_second_run(conn):
    migrate_notebook.run(conn)
    result2 = migrate_notebook.run(conn)
    assert result2["skipped"] is True
    assert conn.execute("SELECT COUNT(*) FROM experiments").fetchone()[0] == 41
