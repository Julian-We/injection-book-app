import sqlite3

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse

from .. import lines
from ..db import get_db
from ..templating import templates
from .plasmids import find_plasmid, get_or_create_plasmid

router = APIRouter()


def _experiment_id_for_mix(conn: sqlite3.Connection, mix_id: int) -> int:
    row = conn.execute("SELECT experiment_id FROM mixes WHERE id = ?", (mix_id,)).fetchone()
    return row["experiment_id"]


def _experiment_id_for_line(conn: sqlite3.Connection, line_id: int) -> int:
    row = conn.execute(
        """SELECT m.experiment_id FROM mix_lines ml
           JOIN mixes m ON ml.mix_id = m.id WHERE ml.id = ?""",
        (line_id,),
    ).fetchone()
    return row["experiment_id"]


def _optional_int(value: str) -> int | None:
    value = (value or "").strip()
    return int(value) if value.isdigit() else None


@router.post("/experiments/{experiment_id}/mixes")
def add_mix(
    experiment_id: int,
    label: str = Form(...),
    preset_id: str = Form(""),
    conn: sqlite3.Connection = Depends(get_db),
):
    count = conn.execute(
        "SELECT COUNT(*) FROM mixes WHERE experiment_id = ?", (experiment_id,)
    ).fetchone()[0]
    cur = conn.execute(
        "INSERT INTO mixes (experiment_id, label, ordering) VALUES (?, ?, ?)",
        (experiment_id, label, count),
    )
    preset = _optional_int(preset_id)
    if preset is not None:
        lines.copy_preset_into_mix(conn, preset, cur.lastrowid)
    conn.commit()
    return RedirectResponse(url=f"/experiments/{experiment_id}", status_code=303)


@router.post("/mixes/{mix_id}/apply_preset")
def apply_preset(
    mix_id: int,
    preset_id: int = Form(...),
    conn: sqlite3.Connection = Depends(get_db),
):
    experiment_id = _experiment_id_for_mix(conn, mix_id)
    lines.copy_preset_into_mix(conn, preset_id, mix_id)
    conn.commit()
    return RedirectResponse(url=f"/experiments/{experiment_id}", status_code=303)


@router.post("/mixes/{mix_id}/lines")
def add_line(
    request: Request,
    mix_id: int,
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
    experiment_id = _experiment_id_for_mix(conn, mix_id)

    if kind == "plasmid":
        construct_id = construct_id.strip()
        row = find_plasmid(conn, construct_id)
        if row is None:
            # Construct number not found in the plasmid database - prompt to add it,
            # carrying the pending line's values through as hidden fields.
            return templates.TemplateResponse(
                "plasmid_not_found.html",
                {
                    "request": request,
                    "form_action": f"/mixes/{mix_id}/lines/confirm_new_plasmid",
                    "cancel_url": f"/experiments/{experiment_id}",
                    "target_label": "mix line",
                    "construct_id": construct_id,
                    "inject_amount": inject_amount, "stock_conc": stock_conc,
                    "inject_volume": inject_volume, "mix_volume_at_calc": mix_volume_at_calc,
                },
            )
        lines.insert_plasmid_line(
            conn, "mix_lines", mix_id, row["id"],
            inject_amount, stock_conc, inject_volume, mix_volume_at_calc,
        )
    else:
        lines.insert_reagent_line(conn, "mix_lines", mix_id, display_text, manual_volume)
    conn.commit()
    return RedirectResponse(url=f"/experiments/{experiment_id}", status_code=303)


@router.post("/mixes/{mix_id}/lines/confirm_new_plasmid")
def confirm_new_plasmid_and_add_line(
    mix_id: int,
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
    experiment_id = _experiment_id_for_mix(conn, mix_id)
    plasmid_id = get_or_create_plasmid(conn, construct_id, name, generated_by, enzyme)
    lines.insert_plasmid_line(
        conn, "mix_lines", mix_id, plasmid_id,
        inject_amount, stock_conc, inject_volume, mix_volume_at_calc,
    )
    conn.commit()
    return RedirectResponse(url=f"/experiments/{experiment_id}", status_code=303)


@router.post("/mix_lines/{line_id}/edit")
def edit_line(
    line_id: int,
    inject_amount: float | None = Form(None),
    stock_conc: float | None = Form(None),
    inject_volume: float = Form(2),
    mix_volume_at_calc: float = Form(3),
    display_text: str = Form(""),
    manual_volume: float | None = Form(None),
    conn: sqlite3.Connection = Depends(get_db),
):
    experiment_id = _experiment_id_for_line(conn, line_id)
    lines.update_line(
        conn, "mix_lines", line_id,
        inject_amount=inject_amount, stock_conc=stock_conc, inject_volume=inject_volume,
        mix_volume_at_calc=mix_volume_at_calc, display_text=display_text, manual_volume=manual_volume,
    )
    conn.commit()
    return RedirectResponse(url=f"/experiments/{experiment_id}", status_code=303)


@router.post("/mix_lines/{line_id}/delete")
def delete_line(line_id: int, conn: sqlite3.Connection = Depends(get_db)):
    experiment_id = _experiment_id_for_line(conn, line_id)
    conn.execute("DELETE FROM mix_lines WHERE id = ?", (line_id,))
    conn.commit()
    return RedirectResponse(url=f"/experiments/{experiment_id}", status_code=303)


@router.post("/mixes/{mix_id}/settings")
def update_mix_settings(
    mix_id: int,
    mix_volume: float = Form(3),
    phr_enabled: bool = Form(False),
    phr_volume: str = Form(""),
    conn: sqlite3.Connection = Depends(get_db),
):
    experiment_id = _experiment_id_for_mix(conn, mix_id)
    try:
        phr_vol = float(phr_volume) if phr_volume.strip() else None  # empty = 10% default
    except ValueError:
        phr_vol = None
    conn.execute(
        """UPDATE mixes SET mix_volume = ?, phr_enabled = ?, phr_volume = ?,
           updated_at = datetime('now') WHERE id = ?""",
        (mix_volume, int(phr_enabled), phr_vol, mix_id),
    )
    conn.commit()
    return RedirectResponse(url=f"/experiments/{experiment_id}", status_code=303)


@router.post("/mixes/{mix_id}/delete")
def delete_mix(mix_id: int, conn: sqlite3.Connection = Depends(get_db)):
    experiment_id = _experiment_id_for_mix(conn, mix_id)
    conn.execute("DELETE FROM mixes WHERE id = ?", (mix_id,))
    conn.commit()
    return RedirectResponse(url=f"/experiments/{experiment_id}", status_code=303)
