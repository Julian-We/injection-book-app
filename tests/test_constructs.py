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
        "INSERT INTO plasmids (construct_id, raw_id_original, name, generated_by) VALUES (?, ?, ?, ?)",
        [("F126", "F126", "pCS2+gfp", "Anna"), ("B465", "B465", "pCS2+mcherry", "Ben")],
    )
    conn.execute("INSERT INTO experiments (slug) VALUES ('test')")
    conn.execute("INSERT INTO mixes (experiment_id, label) VALUES (1, 'testa')")
    conn.commit()
    conn.close()
    yield TestClient(app, follow_redirects=False)


def query(sql, params=()):
    conn = db.get_connection()
    try:
        return conn.execute(sql, params).fetchall()
    finally:
        conn.close()


def plasmid_id(construct_id):
    return query("SELECT id FROM plasmids WHERE construct_id = ?", (construct_id,))[0]["id"]


def test_list_and_search_case_insensitive(client):
    page = client.get("/plasmids", params={"q": "GFP"}).text
    assert "F126" in page and "B465" not in page
    assert "B465" in client.get("/plasmids", params={"q": "ben"}).text
    assert client.get("/plasmids").status_code == 200


def test_add_and_duplicate(client):
    r = client.post("/plasmids", data={"construct_id": "Z1", "name": "new"})
    assert "message=" in r.headers["location"]
    assert query("SELECT source FROM plasmids WHERE construct_id = 'Z1'")[0][0] == "user_added"
    r = client.post("/plasmids", data={"construct_id": "f126", "name": "dup"})
    assert "error=" in r.headers["location"]
    assert "already exists" in client.get(r.headers["location"]).text


def test_edit_name_and_id(client):
    pid = plasmid_id("F126")
    client.post(f"/plasmids/{pid}/edit",
                data={"construct_id": "F126b", "name": "renamed", "generated_by": "", "enzyme": "NotI"})
    row = query("SELECT * FROM plasmids WHERE id = ?", (pid,))[0]
    assert (row["construct_id"], row["name"], row["enzyme"]) == ("F126b", "renamed", "NotI")


def test_edit_to_duplicate_id_refused(client):
    pid = plasmid_id("F126")
    r = client.post(f"/plasmids/{pid}/edit", data={"construct_id": "b465", "name": "x"})
    assert "error=" in r.headers["location"]
    assert query("SELECT construct_id FROM plasmids WHERE id = ?", (pid,))[0][0] == "F126"


def test_edit_keeps_own_id_with_different_case(client):
    pid = plasmid_id("F126")
    r = client.post(f"/plasmids/{pid}/edit", data={"construct_id": "f126", "name": "x"})
    assert "error=" not in r.headers["location"]


def test_delete_unused_and_refuse_used(client):
    client.post("/mixes/1/lines", data={"kind": "plasmid", "construct_id": "B465",
                                        "inject_amount": 100, "stock_conc": 500})
    r = client.post(f"/plasmids/{plasmid_id('B465')}/delete")
    assert "error=" in r.headers["location"]
    assert query("SELECT COUNT(*) FROM plasmids WHERE construct_id = 'B465'")[0][0] == 1
    client.post(f"/plasmids/{plasmid_id('F126')}/delete")
    assert query("SELECT COUNT(*) FROM plasmids WHERE construct_id = 'F126'")[0][0] == 0


def test_mix_phr_volume_setting(client):
    client.post("/mixes/1/settings", data={"mix_volume": 3, "phr_enabled": "true", "phr_volume": "0.5"})
    assert query("SELECT phr_volume FROM mixes WHERE id = 1")[0][0] == 0.5
    page = client.get("/experiments/1").text
    assert "PhR 0.5 µL" in page
    assert "<td>2.5</td>" in page  # HEPES = 3 - 0.5
    client.post("/mixes/1/settings", data={"mix_volume": 3, "phr_enabled": "true", "phr_volume": ""})
    assert query("SELECT phr_volume FROM mixes WHERE id = 1")[0][0] is None
    assert "PhR 0.3 µL" in client.get("/experiments/1").text
