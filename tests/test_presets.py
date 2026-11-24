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
    conn.executemany(
        "INSERT INTO plasmids (construct_id, raw_id_original, name) VALUES (?, ?, ?)",
        [("F126", "F126", "pCS2+gfp"), ("B465", "B465", "pCS2+mcherry")],
    )
    conn.execute("INSERT INTO experiments (slug) VALUES ('test')")
    conn.execute("INSERT INTO mixes (experiment_id, label) VALUES (1, 'testa')")
    conn.commit()
    conn.close()
    # Not used as a context manager, so the lifespan (CSV/notebook import) doesn't run.
    yield TestClient(app, follow_redirects=False)


def query(sql, params=()):
    conn = db.get_connection()
    try:
        return conn.execute(sql, params).fetchall()
    finally:
        conn.close()


def add_plasmid_line(client, url, construct_id, amount=100, conc=500):
    return client.post(url, data={
        "kind": "plasmid", "construct_id": construct_id,
        "inject_amount": amount, "stock_conc": conc,
    })


def make_preset(client):
    r = client.post("/presets", data={"name": "Conversion factors"})
    assert r.status_code == 303
    preset_id = int(r.headers["location"].rsplit("/", 1)[1])
    add_plasmid_line(client, f"/presets/{preset_id}/lines", "F126", amount=50, conc=200)
    add_plasmid_line(client, f"/presets/{preset_id}/lines", "b465", amount=80, conc=952)
    client.post(f"/presets/{preset_id}/lines",
                data={"kind": "reagent", "display_text": "MO #27", "manual_volume": 0.5})
    return preset_id


def test_construct_lookup_is_case_insensitive(client):
    r = add_plasmid_line(client, "/mixes/1/lines", "  f126 ")
    assert r.status_code == 303  # redirected back, not the "not found" page
    rows = query("SELECT p.construct_id FROM mix_lines ml JOIN plasmids p ON ml.plasmid_id = p.id")
    assert [r["construct_id"] for r in rows] == ["F126"]
    assert client.get("/api/plasmids/lookup", params={"construct_id": "f126"}).json()["found"]


def test_adding_lowercase_id_does_not_duplicate_plasmid(client):
    client.post("/api/plasmids", data={"construct_id": "f126", "name": "dup"})
    assert len(query("SELECT * FROM plasmids WHERE construct_id = 'F126' COLLATE NOCASE")) == 1


def test_apply_preset_appends_copies_after_existing_lines(client):
    preset_id = make_preset(client)
    add_plasmid_line(client, "/mixes/1/lines", "B465")  # existing marker line
    r = client.post("/mixes/1/apply_preset", data={"preset_id": preset_id})
    assert r.status_code == 303
    rows = query("SELECT * FROM mix_lines WHERE mix_id = 1 ORDER BY ordering")
    assert len(rows) == 4
    assert [r["ordering"] for r in rows] == [0, 1, 2, 3]
    assert (rows[1]["inject_amount"], rows[1]["stock_conc"]) == (50, 200)
    assert rows[3]["kind"] == "reagent" and rows[3]["display_name_override"] == "MO #27"
    assert client.get("/experiments/1").status_code == 200


def test_new_mix_from_preset(client):
    preset_id = make_preset(client)
    client.post("/experiments/1/mixes", data={"label": "testb", "preset_id": str(preset_id)})
    client.post("/experiments/1/mixes", data={"label": "testc", "preset_id": ""})
    counts = query("""SELECT m.label, COUNT(ml.id) AS n FROM mixes m
                      LEFT JOIN mix_lines ml ON ml.mix_id = m.id GROUP BY m.id ORDER BY m.id""")
    assert [(c["label"], c["n"]) for c in counts] == [("testa", 0), ("testb", 3), ("testc", 0)]


def test_editing_mix_line_leaves_preset_unchanged(client):
    preset_id = make_preset(client)
    client.post("/mixes/1/apply_preset", data={"preset_id": preset_id})
    line_id = query("SELECT id FROM mix_lines WHERE mix_id = 1 ORDER BY ordering")[0]["id"]
    client.post(f"/mix_lines/{line_id}/edit",
                data={"inject_amount": 999, "stock_conc": 300, "inject_volume": 2, "mix_volume_at_calc": 3})
    assert query("SELECT inject_amount FROM mix_lines WHERE id = ?", (line_id,))[0][0] == 999
    preset_amounts = [r[0] for r in query(
        "SELECT inject_amount FROM preset_lines WHERE preset_id = ? ORDER BY ordering", (preset_id,))]
    assert preset_amounts == [50, 80, None]


def test_edit_reagent_line(client):
    preset_id = make_preset(client)
    line_id = query("SELECT id FROM preset_lines WHERE kind = 'reagent'")[0]["id"]
    client.post(f"/preset_lines/{line_id}/edit", data={"display_text": "MO #28", "manual_volume": 0.7})
    row = query("SELECT * FROM preset_lines WHERE id = ?", (line_id,))[0]
    assert (row["display_name_override"], row["manual_volume"]) == ("MO #28", 0.7)
    assert client.get(f"/presets/{preset_id}").status_code == 200


def test_unknown_construct_in_preset_prompts_then_adds(client):
    preset_id = make_preset(client)
    r = add_plasmid_line(client, f"/presets/{preset_id}/lines", "Z999")
    assert r.status_code == 200 and f"/presets/{preset_id}/lines/confirm_new_plasmid" in r.text
    client.post(f"/presets/{preset_id}/lines/confirm_new_plasmid", data={
        "construct_id": "Z999", "name": "new", "inject_amount": 10, "stock_conc": 100,
    })
    assert len(query("SELECT * FROM preset_lines WHERE preset_id = ?", (preset_id,))) == 4


def test_delete_preset_cascades_but_keeps_mix_lines(client):
    preset_id = make_preset(client)
    client.post("/mixes/1/apply_preset", data={"preset_id": preset_id})
    client.post(f"/presets/{preset_id}/delete")
    assert query("SELECT COUNT(*) FROM preset_lines")[0][0] == 0
    assert query("SELECT COUNT(*) FROM mix_lines")[0][0] == 3


def test_duplicate_preset_name_shows_error(client):
    client.post("/presets", data={"name": "A"})
    r = client.post("/presets", data={"name": "A"})
    assert "error=" in r.headers["location"]
    assert "already exists" in client.get(r.headers["location"]).text
