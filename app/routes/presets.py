import sqlite3

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse

from .. import lines
from ..db import get_db
from ..templating import templates
from .plasmids import find_plasmid, get_or_create_plasmid

router = APIRouter()


def _preset_id_for_line(conn: sqlite3.Connection, line_id: int) -> int:
    return conn.execute(
        "SELECT preset_id FROM preset_lines WHERE id = ?", (line_id,)
    ).fetchone()["preset_id"]


def list_presets(conn: sqlite3.Connection):
    return conn.execute(
        """SELECT p.*, COUNT(pl.id) AS line_count
           FROM presets p LEFT JOIN preset_lines pl ON pl.preset_id = p.id
           GROUP BY p.id ORDER BY p.name COLLATE NOCASE"""
    ).fetchall()


@router.get("/presets")
def presets_index(request: Request, conn: sqlite3.Connection = Depends(get_db)):
    return templates.TemplateResponse(
        "presets_list.html",
        {"request": request, "presets": list_presets(conn), "error": request.query_params.get("error")},
    )


@router.post("/presets")
def create_preset(
    name: str = Form(...),
    description: str = Form(""),
    conn: sqlite3.Connection = Depends(get_db),
):
    try:
        cur = conn.execute(
            "INSERT INTO presets (name, description) VALUES (?, ?)",
            (name.strip(), description.strip()),
        )
    except sqlite3.IntegrityError:
        return RedirectResponse(url="/presets?error=A+preset+with+this+name+already+exists", status_code=303)
    conn.commit()
    return RedirectResponse(url=f"/presets/{cur.lastrowid}", status_code=303)


@router.get("/presets/{preset_id}")
def preset_detail(request: Request, preset_id: int, conn: sqlite3.Connection = Depends(get_db)):
    preset = conn.execute("SELECT * FROM presets WHERE id = ?", (preset_id,)).fetchone()
    if preset is None:
        return RedirectResponse(url="/presets", status_code=303)
    preset_lines = conn.execute(
        """SELECT pl.*, p.name AS plasmid_name, p.construct_id AS plasmid_construct_id
           FROM preset_lines pl LEFT JOIN plasmids p ON pl.plasmid_id = p.id
           WHERE pl.preset_id = ? ORDER BY pl.ordering""",
        (preset_id,),
    ).fetchall()
    return templates.TemplateResponse(
        "preset_detail.html",
        {"request": request, "preset": preset, "lines": preset_lines,
         "error": request.query_params.get("error")},
    )


@router.post("/presets/{preset_id}/edit")
def edit_preset(
    preset_id: int,
    name: str = Form(...),
    description: str = Form(""),
    conn: sqlite3.Connection = Depends(get_db),
):
    try:
        conn.execute(
            "UPDATE presets SET name = ?, description = ?, updated_at = datetime('now') WHERE id = ?",
            (name.strip(), description.strip(), preset_id),
        )
    except sqlite3.IntegrityError:
        return RedirectResponse(
            url=f"/presets/{preset_id}?error=A+preset+with+this+name+already+exists", status_code=303
        )
    conn.commit()
    return RedirectResponse(url=f"/presets/{preset_id}", status_code=303)


@router.post("/presets/{preset_id}/delete")
def delete_preset(preset_id: int, conn: sqlite3.Connection = Depends(get_db)):
    conn.execute("DELETE FROM presets WHERE id = ?", (preset_id,))
    conn.commit()
    return RedirectResponse(url="/presets", status_code=303)


@router.post("/presets/{preset_id}/lines")
def add_preset_line(
    request: Request,
    preset_id: int,
    kind: str = Form(...),
    construct_id: str = Form(""),
    inject_amount: float | None = Form(None),
    stock_conc: float | None = Form(None),
    inject_volume: float = Form(2),
    mix_volume_at_calc: float = Form(3),
    display_text: str = Form(""),
    manual_volume: float | None = Form(None),
    conn: sqlite3.Connection = Depends(get_db),
):
    if kind == "plasmid":
        construct_id = construct_id.strip()
        row = find_plasmid(conn, construct_id)
        if row is None:
            return templates.TemplateResponse(
                "plasmid_not_found.html",
                {
                    "request": request,
                    "form_action": f"/presets/{preset_id}/lines/confirm_new_plasmid",
                    "cancel_url": f"/presets/{preset_id}",
                    "target_label": "preset line",
                    "construct_id": construct_id,
                    "inject_amount": inject_amount, "stock_conc": stock_conc,
                    "inject_volume": inject_volume, "mix_volume_at_calc": mix_volume_at_calc,
                },
            )
        lines.insert_plasmid_line(
            conn, "preset_lines", preset_id, row["id"],
            inject_amount, stock_conc, inject_volume, mix_volume_at_calc,
        )
    else:
        lines.insert_reagent_line(conn, "preset_lines", preset_id, display_text, manual_volume)
    conn.commit()
    return RedirectResponse(url=f"/presets/{preset_id}", status_code=303)


@router.post("/presets/{preset_id}/lines/confirm_new_plasmid")
def confirm_new_plasmid_and_add_preset_line(
    preset_id: int,
    construct_id: str = Form(...),
    name: str = Form(...),
    generated_by: str = Form(""),
    enzyme: str = Form(""),
    inject_amount: float = Form(...),
    stock_conc: float = Form(...),
    inject_volume: float = Form(2),
    mix_volume_at_calc: float = Form(3),
    conn: sqlite3.Connection = Depends(get_db),
):
    plasmid_id = get_or_create_plasmid(conn, construct_id, name, generated_by, enzyme)
    lines.insert_plasmid_line(
        conn, "preset_lines", preset_id, plasmid_id,
        inject_amount, stock_conc, inject_volume, mix_volume_at_calc,
    )
    conn.commit()
    return RedirectResponse(url=f"/presets/{preset_id}", status_code=303)


@router.post("/preset_lines/{line_id}/edit")
def edit_preset_line(
    line_id: int,
    inject_amount: float | None = Form(None),
    stock_conc: float | None = Form(None),
    inject_volume: float = Form(2),
    mix_volume_at_calc: float = Form(3),
    display_text: str = Form(""),
    manual_volume: float | None = Form(None),
    conn: sqlite3.Connection = Depends(get_db),
):
    preset_id = _preset_id_for_line(conn, line_id)
    lines.update_line(
        conn, "preset_lines", line_id,
        inject_amount=inject_amount, stock_conc=stock_conc, inject_volume=inject_volume,
        mix_volume_at_calc=mix_volume_at_calc, display_text=display_text, manual_volume=manual_volume,
    )
    conn.commit()
    return RedirectResponse(url=f"/presets/{preset_id}", status_code=303)


@router.post("/preset_lines/{line_id}/delete")
def delete_preset_line(line_id: int, conn: sqlite3.Connection = Depends(get_db)):
    preset_id = _preset_id_for_line(conn, line_id)
    conn.execute("DELETE FROM preset_lines WHERE id = ?", (line_id,))
    conn.commit()
    return RedirectResponse(url=f"/presets/{preset_id}", status_code=303)
