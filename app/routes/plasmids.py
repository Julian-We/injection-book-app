import sqlite3
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import JSONResponse, RedirectResponse

from ..db import get_db
from ..templating import templates

router = APIRouter()


def find_plasmid(conn: sqlite3.Connection, construct_id: str):
    """Look up a plasmid by construct ID, ignoring case and surrounding whitespace."""
    return conn.execute(
        "SELECT * FROM plasmids WHERE construct_id = ? COLLATE NOCASE",
        (construct_id.strip(),),
    ).fetchone()


def get_or_create_plasmid(
    conn: sqlite3.Connection, construct_id: str, name: str, generated_by: str = "", enzyme: str = ""
) -> int:
    """Return the id of the plasmid with this construct ID, adding it (user_added) if missing."""
    existing = find_plasmid(conn, construct_id)
    if existing is not None:
        return existing["id"]
    construct_id = construct_id.strip()
    cur = conn.execute(
        """INSERT INTO plasmids (construct_id, raw_id_original, name, generated_by, enzyme, enzyme_raw, source)
           VALUES (?, ?, ?, ?, ?, ?, 'user_added')""",
        (construct_id, construct_id, name.strip(), generated_by.strip(), enzyme.strip(), enzyme.strip()),
    )
    return cur.lastrowid


@router.get("/api/plasmids/lookup")
def lookup_plasmid(construct_id: str, conn: sqlite3.Connection = Depends(get_db)):
    construct_id = construct_id.strip()
    row = find_plasmid(conn, construct_id)
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
    get_or_create_plasmid(conn, construct_id, name, generated_by, enzyme)
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


# --- Construct database editor (/plasmids) ---------------------------------

PAGE_SIZE = 50


def _back_to_list(q: str, page: int, **extra) -> RedirectResponse:
    params = {k: v for k, v in {"q": q, "page": page if page > 1 else "", **extra}.items() if v}
    url = "/plasmids" + (f"?{urlencode(params)}" if params else "")
    return RedirectResponse(url=url, status_code=303)


def _usage_count(conn: sqlite3.Connection, plasmid_id: int) -> int:
    return conn.execute(
        """SELECT (SELECT COUNT(*) FROM mix_lines WHERE plasmid_id = ?)
                + (SELECT COUNT(*) FROM preset_lines WHERE plasmid_id = ?)""",
        (plasmid_id, plasmid_id),
    ).fetchone()[0]


@router.get("/plasmids")
def plasmids_index(request: Request, q: str = "", page: int = 1, conn: sqlite3.Connection = Depends(get_db)):
    q = q.strip()
    page = max(page, 1)
    where, params = "", []
    if q:
        like = f"%{q}%"
        where = "WHERE p.construct_id LIKE ? OR p.name LIKE ? OR p.generated_by LIKE ?"
        params = [like, like, like]
    total = conn.execute(f"SELECT COUNT(*) FROM plasmids p {where}", params).fetchone()[0]
    pages = max((total + PAGE_SIZE - 1) // PAGE_SIZE, 1)
    page = min(page, pages)
    rows = conn.execute(
        f"""SELECT p.*,
                   (SELECT COUNT(*) FROM mix_lines ml WHERE ml.plasmid_id = p.id)
                 + (SELECT COUNT(*) FROM preset_lines pl WHERE pl.plasmid_id = p.id) AS usage_count
            FROM plasmids p {where}
            ORDER BY p.construct_id COLLATE NOCASE
            LIMIT ? OFFSET ?""",
        [*params, PAGE_SIZE, (page - 1) * PAGE_SIZE],
    ).fetchall()
    return templates.TemplateResponse(
        "plasmids_list.html",
        {
            "request": request, "plasmids": rows, "q": q, "page": page, "pages": pages, "total": total,
            "error": request.query_params.get("error"), "message": request.query_params.get("message"),
        },
    )


@router.post("/plasmids")
def create_plasmid(
    construct_id: str = Form(...),
    name: str = Form(...),
    generated_by: str = Form(""),
    enzyme: str = Form(""),
    q: str = Form(""),
    page: int = Form(1),
    conn: sqlite3.Connection = Depends(get_db),
):
    construct_id = construct_id.strip()
    if not construct_id:
        return _back_to_list(q, page, error="Construct ID must not be empty")
    existing = find_plasmid(conn, construct_id)
    if existing is not None:
        return _back_to_list(q, page, error=f"Construct ID {existing['construct_id']} already exists")
    get_or_create_plasmid(conn, construct_id, name, generated_by, enzyme)
    conn.commit()
    return _back_to_list(construct_id, 1, message=f"Added {construct_id}")


@router.post("/plasmids/{plasmid_id}/edit")
def edit_plasmid(
    plasmid_id: int,
    construct_id: str = Form(...),
    name: str = Form(""),
    generated_by: str = Form(""),
    enzyme: str = Form(""),
    q: str = Form(""),
    page: int = Form(1),
    conn: sqlite3.Connection = Depends(get_db),
):
    construct_id = construct_id.strip()
    if not construct_id:
        return _back_to_list(q, page, error="Construct ID must not be empty")
    clash = conn.execute(
        "SELECT construct_id FROM plasmids WHERE construct_id = ? COLLATE NOCASE AND id != ?",
        (construct_id, plasmid_id),
    ).fetchone()
    if clash is not None:
        return _back_to_list(q, page, error=f"Construct ID {clash['construct_id']} is already used by another construct")
    conn.execute(
        """UPDATE plasmids SET construct_id = ?, name = ?, generated_by = ?, enzyme = ?,
           updated_at = datetime('now') WHERE id = ?""",
        (construct_id, name.strip(), generated_by.strip(), enzyme.strip(), plasmid_id),
    )
    conn.commit()
    return _back_to_list(q, page, message=f"Saved {construct_id}")


@router.post("/plasmids/{plasmid_id}/delete")
def delete_plasmid(
    plasmid_id: int,
    q: str = Form(""),
    page: int = Form(1),
    conn: sqlite3.Connection = Depends(get_db),
):
    row = conn.execute("SELECT construct_id FROM plasmids WHERE id = ?", (plasmid_id,)).fetchone()
    if row is None:
        return _back_to_list(q, page)
    used = _usage_count(conn, plasmid_id)
    if used:
        return _back_to_list(
            q, page, error=f"{row['construct_id']} is used in {used} mix/preset line(s) and can't be deleted"
        )
    conn.execute("DELETE FROM plasmids WHERE id = ?", (plasmid_id,))
    conn.commit()
    return _back_to_list(q, page, message=f"Deleted {row['construct_id']}")
