import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import db  # noqa: E402
from app.lines import suggest_duplicate_label  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "test.db"))
    conn = db.get_connection()
    db.ensure_schema(conn)
    conn.executemany(
        "INSERT INTO plasmids (construct_id, raw_id_original, name) VALUES (?, ?, ?)",
        [("F126", "F126", "pCS2+gfp"), ("B465", "B465", "pCS2+mcherry")],
    )
    conn.execute("INSERT INTO experiments (slug) VALUES ('test')")
    conn.execute("INSERT INTO mixes (experiment_id, label, mix_volume, phr_volume) VALUES (1, 'jan22a', 4, 0.5)")
    conn.commit()
    conn.close()
    c = TestClient(app, follow_redirects=False)
    c.post("/mixes/1/lines", data={"kind": "plasmid", "construct_id": "F126", "inject_amount": 50, "stock_conc": 200})
    c.post("/mixes/1/lines", data={"kind": "plasmid", "construct_id": "B465", "inject_amount": 80, "stock_conc": 952,
                                   "inject_volume": 6, "mix_volume_at_calc": 4})
    c.post("/mixes/1/lines", data={"kind": "reagent", "display_text": "MO #27", "manual_volume": 0.6})
    yield c


def query(sql, params=()):
    conn = db.get_connection()
    try:
        return conn.execute(sql, params).fetchall()
    finally:
        conn.close()


LINE_COLS = ("ordering", "kind", "plasmid_id", "display_name_override", "inject_amount", "stock_conc",
             "inject_volume", "mix_volume_at_calc", "manual_volume")


def line_values(mix_id):
    return [tuple(r[c] for c in LINE_COLS)
            for r in query("SELECT * FROM mix_lines WHERE mix_id = ? ORDER BY ordering", (mix_id,))]


def test_duplicate_copies_settings_and_lines(client):
    r = client.post("/mixes/1/duplicate", data={"label": "jan22b"})
    assert r.headers["location"] == "/experiments/1#mix-2"
    new = query("SELECT * FROM mixes WHERE id = 2")[0]
    assert (new["experiment_id"], new["label"], new["mix_volume"], new["phr_enabled"], new["phr_volume"]) == \
        (1, "jan22b", 4, 1, 0.5)
    assert line_values(2) == line_values(1)
    assert len(line_values(2)) == 3
    page = client.get("/experiments/1").text
    assert 'id="mix-2"' in page and 'value="jan22c"' in page


def test_editing_copy_leaves_original(client):
    client.post("/mixes/1/duplicate", data={"label": "jan22b"})
    copy_line = query("SELECT id FROM mix_lines WHERE mix_id = 2 ORDER BY ordering")[0]["id"]
    client.post(f"/mix_lines/{copy_line}/edit",
                data={"inject_amount": 999, "stock_conc": 200, "inject_volume": 2, "mix_volume_at_calc": 3})
    assert query("SELECT inject_amount FROM mix_lines WHERE mix_id = 1 ORDER BY ordering")[0][0] == 50
    assert query("SELECT inject_amount FROM mix_lines WHERE id = ?", (copy_line,))[0][0] == 999


def test_review_flags_not_copied(client):
    conn = db.get_connection()
    conn.execute("UPDATE mix_lines SET needs_review = 1, review_note = 'quirk' WHERE mix_id = 1")
    conn.commit()
    conn.close()
    client.post("/mixes/1/duplicate", data={"label": "x"})
    assert query("SELECT SUM(needs_review) FROM mix_lines WHERE mix_id = 2")[0][0] == 0


def test_empty_label_uses_suggestion(client):
    client.post("/mixes/1/duplicate", data={"label": ""})
    client.post("/mixes/1/duplicate", data={"label": "  "})
    assert [r[0] for r in query("SELECT label FROM mixes ORDER BY id")] == ["jan22a", "jan22b", "jan22c"]


@pytest.mark.parametrize("label,existing,expected", [
    ("jan22a", ["jan22a"], "jan22b"),
    ("jan22a", ["jan22a", "jan22b", "JAN22C"], "jan22d"),
    ("jan22B", ["jan22B"], "jan22C"),
    ("a", ["a"], "b"),
    ("jan22z", ["jan22z"], "jan22z copy"),
    ("mix1", ["mix1"], "mix1 copy"),
    ("jan22a copy", ["jan22a copy"], "jan22a copy copy"),
    ("control", ["control", "control copy"], "control copy 2"),
])
def test_suggest_duplicate_label(label, existing, expected):
    assert suggest_duplicate_label(label, existing) == expected
