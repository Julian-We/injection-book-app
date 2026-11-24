import sqlite3

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import JSONResponse

from ..db import get_db
from ..templating import templates

router = APIRouter()


@router.get("/api/plasmids/lookup")
def lookup_plasmid(construct_id: str, conn: sqlite3.Connection = Depends(get_db)):
    construct_id = construct_id.strip()
    row = conn.execute(
        "SELECT construct_id, name, generated_by, enzyme, needs_review FROM plasmids WHERE construct_id = ?",
        (construct_id,),
    ).fetchone()
    if row is None:
        return JSONResponse({"found": False, "construct_id": construct_id})
    return JSONResponse({
        "found": True,
        "construct_id": row["construct_id"],
        "name": row["name"],
        "generated_by": row["generated_by"],
        "enzyme": row["enzyme"],
        "needs_review": bool(row["needs_review"]),
    })


@router.post("/api/plasmids")
def add_plasmid(
    request: Request,
    construct_id: str = Form(...),
    name: str = Form(...),
    generated_by: str = Form(""),
    enzyme: str = Form(""),
    conn: sqlite3.Connection = Depends(get_db),
):
    construct_id = construct_id.strip()
    name = name.strip()
    existing = conn.execute(
        "SELECT id FROM plasmids WHERE construct_id = ?", (construct_id,)
    ).fetchone()
    if existing is None:
        conn.execute(
            """INSERT INTO plasmids (construct_id, raw_id_original, name, generated_by, enzyme, enzyme_raw, source)
               VALUES (?, ?, ?, ?, ?, ?, 'user_added')""",
            (construct_id, construct_id, name, generated_by.strip(), enzyme.strip(), enzyme.strip()),
        )
        conn.commit()
    return JSONResponse({"ok": True, "construct_id": construct_id, "name": name})


@router.get("/plasmids/flagged")
def flagged_review(request: Request, conn: sqlite3.Connection = Depends(get_db)):
    plasmids = conn.execute(
        "SELECT * FROM plasmids WHERE needs_review = 1 ORDER BY construct_id"
    ).fetchall()
    lines = conn.execute(
        """SELECT ml.*, m.label AS mix_label, e.slug AS experiment_slug, e.id AS experiment_id
           FROM mix_lines ml
           JOIN mixes m ON ml.mix_id = m.id
           JOIN experiments e ON m.experiment_id = e.id
           WHERE ml.needs_review = 1
           ORDER BY e.experiment_date"""
    ).fetchall()
    return templates.TemplateResponse(
        "flagged_review.html",
        {"request": request, "plasmids": plasmids, "lines": lines},
    )


@router.post("/plasmids/{plasmid_id}/clear_review")
def clear_plasmid_review(plasmid_id: int, conn: sqlite3.Connection = Depends(get_db)):
    conn.execute(
        "UPDATE plasmids SET needs_review = 0, updated_at = datetime('now') WHERE id = ?",
        (plasmid_id,),
    )
    conn.commit()
    return JSONResponse({"ok": True})


@router.post("/mix_lines/{line_id}/clear_review")
def clear_line_review(line_id: int, conn: sqlite3.Connection = Depends(get_db)):
    conn.execute(
        "UPDATE mix_lines SET needs_review = 0, updated_at = datetime('now') WHERE id = ?",
        (line_id,),
    )
    conn.commit()
    return JSONResponse({"ok": True})
