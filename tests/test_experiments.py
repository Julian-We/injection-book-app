import sqlite3
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import db  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "test.db"))
    conn = db.get_connection()
    db.ensure_schema(conn)
    conn.close()
    yield TestClient(app, follow_redirects=False)


def create(client, exp_title, date, **extra):
    return client.post("/experiments", data={"slug": exp_title, "experiment_date": date, **extra})


def experiment_id(response):
    return int(response.headers["location"].rsplit("/", 1)[1])


def test_export_filename_uses_space(client):
    eid = experiment_id(create(client, "heatshock timelapse test", "2026-10-06"))
    r = client.get(f"/experiments/{eid}/export.md")
    assert r.status_code == 200
    assert 'filename="20261006 heatshock timelapse test.md"' in r.headers["content-disposition"]


def test_export_title_already_starting_with_date_is_not_doubled(client):
    eid = experiment_id(create(client, "20250808 RNA longevity", "2025-08-08"))
    cd = client.get(f"/experiments/{eid}/export.md").headers["content-disposition"]
    assert 'filename="20250808 RNA longevity.md"' in cd


def test_export_non_ascii_title(client):
    eid = experiment_id(create(client, "CaAR reaction – trial 1", "2025-10-23"))
    r = client.get(f"/experiments/{eid}/export.md")
    assert r.status_code == 200
    cd = r.headers["content-disposition"]
    assert "filename*=UTF-8''20251023%20CaAR%20reaction%20%E2%80%93%20trial%201.md" in cd
    assert 'filename="20251023 CaAR reaction _ trial 1.md"' in cd


def test_export_slash_in_title_is_replaced(client):
    eid = experiment_id(create(client, "GFP/mCherry test", "2026-01-02"))
    cd = client.get(f"/experiments/{eid}/export.md").headers["content-disposition"]
    assert 'filename="20260102 GFP-mCherry test.md"' in cd


def test_description_goes_under_aim(client):
    eid = experiment_id(create(client, "x", "2026-01-02", title="Check heatshock response"))
    assert "# Aim of experiment\nCheck heatshock response\n" in client.get(f"/experiments/{eid}/export.md").text


def test_same_title_on_different_dates_allowed(client):
    assert create(client, "heatshock timelapse test", "2026-10-06").status_code == 303
    assert create(client, "heatshock timelapse test", "2026-10-13").status_code == 303


def test_same_title_same_date_shows_error(client):
    create(client, "heatshock timelapse test", "2026-10-06")
    r = create(client, "heatshock timelapse test", "2026-10-06", title="my description")
    assert r.status_code == 400
    assert "already exists on this date" in r.text
    assert 'value="my description"' in r.text  # entered values are kept


def test_edit_to_clashing_title_shows_error(client):
    create(client, "a", "2026-10-06")
    eid = experiment_id(create(client, "b", "2026-10-06"))
    r = client.post(f"/experiments/{eid}/edit", data={"slug": "a", "experiment_date": "2026-10-06"})
    assert r.status_code == 400 and "already exists on this date" in r.text
    assert f'action="/experiments/{eid}/edit"' in r.text


def test_form_labels(client):
    page = client.get("/experiments/new").text
    assert "Title<br>" in page and "Description / aim of experiment" in page and "Slug" not in page


# --- migration of older databases -------------------------------------------

OLD_EXPERIMENTS_TABLE = """
CREATE TABLE experiments (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    slug              TEXT NOT NULL UNIQUE,
    title             TEXT,
    experiment_group  TEXT,
    repetition        TEXT,
    tags              TEXT NOT NULL DEFAULT '#Labbook',
    injection_stage   TEXT,
    incubation_at     TEXT,
    experiment_date   TEXT,
    source            TEXT NOT NULL DEFAULT 'app_created',
    source_label      TEXT,
    migration_note    TEXT,
    created_at        TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at        TEXT NOT NULL DEFAULT (datetime('now'))
);
"""


@pytest.fixture
def old_db(tmp_path, monkeypatch):
    """A database created before this change: slug UNIQUE, and no closed_at column yet."""
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "old.db"))
    conn = db.get_connection()
    conn.executescript(OLD_EXPERIMENTS_TABLE)
    schema = db.SCHEMA_PATH.read_text()
    start = schema.index("CREATE TABLE IF NOT EXISTS experiments")
    end = schema.index("-- mixes:")
    conn.executescript(schema[:start] + schema[end:])  # everything except experiments
    conn.execute("INSERT INTO experiments (id, slug, experiment_date) VALUES (5, 'heatshock', '2026-10-06')")
    conn.execute("INSERT INTO experiments (id, slug, experiment_date) VALUES (9, 'other', '2026-10-07')")
    conn.execute("INSERT INTO mixes (id, experiment_id, label) VALUES (1, 5, 'a'), (2, 5, 'b'), (3, 9, 'a')")
    conn.execute("INSERT INTO mix_lines (mix_id, ordering, kind, manual_volume) VALUES (1, 0, 'reagent', 0.5)")
    conn.commit()
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("INSERT INTO experiments (slug, experiment_date) VALUES ('heatshock', '2026-10-13')")
    conn.rollback()
    yield conn
    conn.close()


def test_migration_relaxes_unique_and_keeps_data(old_db):
    db.ensure_schema(old_db)
    rows = old_db.execute("SELECT id, slug, experiment_date FROM experiments ORDER BY id").fetchall()
    assert [tuple(r) for r in rows] == [(5, "heatshock", "2026-10-06"), (9, "other", "2026-10-07")]
    assert old_db.execute("SELECT COUNT(*) FROM mixes").fetchone()[0] == 3
    assert old_db.execute("SELECT COUNT(*) FROM mix_lines").fetchone()[0] == 1
    # same title on another date now works, same title + same date still doesn't
    old_db.execute("INSERT INTO experiments (slug, experiment_date) VALUES ('heatshock', '2026-10-13')")
    with pytest.raises(sqlite3.IntegrityError):
        old_db.execute("INSERT INTO experiments (slug, experiment_date) VALUES ('heatshock', '2026-10-06')")
    # foreign keys still work: deleting an experiment cascades to its mixes and lines
    assert old_db.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    old_db.execute("DELETE FROM experiments WHERE id = 5")
    assert old_db.execute("SELECT COUNT(*) FROM mixes").fetchone()[0] == 1
    assert old_db.execute("SELECT COUNT(*) FROM mix_lines").fetchone()[0] == 0
    # closed_at column was added too
    assert "closed_at" in [r[1] for r in old_db.execute("PRAGMA table_info(experiments)")]


def test_migration_is_idempotent(old_db):
    db.ensure_schema(old_db)
    sql_before = old_db.execute("SELECT sql FROM sqlite_master WHERE name = 'experiments'").fetchone()[0]
    db.ensure_schema(old_db)
    sql_after = old_db.execute("SELECT sql FROM sqlite_master WHERE name = 'experiments'").fetchone()[0]
    assert sql_before == sql_after
    assert "UNIQUE(slug, experiment_date)" in sql_after
