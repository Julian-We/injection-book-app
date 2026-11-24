import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db import ensure_schema  # noqa: E402
from migrations import migrate_plasmids  # noqa: E402

SOURCE_ROW_COUNT = 6478
# Hard-coded, independent of the migration script's own enumeration - the exact
# set of rows known (from manual inspection of plasmid_db.csv) to need review.
EXPECTED_FLAGGED_IDS = {
    "4??", "b\x0b875", "D761.", "E163.", "E575\x0bE575", "E773\x0bE773",
    "E855 EGFP-tdrd7a w/o domain1.tdrd7-3’UTR", "E884 EGFP-", "e958", "e964",
}


@pytest.fixture
def conn():
    c = sqlite3.connect(":memory:")
    c.row_factory = sqlite3.Row
    ensure_schema(c)
    yield c
    c.close()


def test_imports_every_row_without_dropping_any(conn):
    result = migrate_plasmids.run(conn)
    assert result["inserted"] == SOURCE_ROW_COUNT
    assert conn.execute("SELECT COUNT(*) FROM plasmids").fetchone()[0] == SOURCE_ROW_COUNT


def test_flagged_rows_match_known_hard_cases(conn):
    migrate_plasmids.run(conn)
    flagged_ids = {
        r["construct_id"] for r in conn.execute(
            "SELECT construct_id FROM plasmids WHERE needs_review = 1"
        )
    }
    assert flagged_ids == EXPECTED_FLAGGED_IDS


def test_c755_pair_kept_as_two_distinct_unflagged_rows(conn):
    migrate_plasmids.run(conn)
    rows = conn.execute(
        "SELECT construct_id, needs_review FROM plasmids WHERE construct_id IN ('C755-1', 'C755-2')"
    ).fetchall()
    assert {r["construct_id"] for r in rows} == {"C755-1", "C755-2"}
    assert all(r["needs_review"] == 0 for r in rows)


def test_known_plasmid_resolves_correctly(conn):
    migrate_plasmids.run(conn)
    row = conn.execute("SELECT name FROM plasmids WHERE construct_id = 'F126'").fetchone()
    assert row["name"] == "paGFP(S66T+G68A).nos3'UTR"


def test_idempotent_on_second_run(conn):
    migrate_plasmids.run(conn)
    result2 = migrate_plasmids.run(conn)
    assert result2["skipped"] is True
    assert conn.execute("SELECT COUNT(*) FROM plasmids").fetchone()[0] == SOURCE_ROW_COUNT
