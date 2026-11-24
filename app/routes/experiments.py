import datetime
import sqlite3

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse, Response

from urllib.parse import quote

from ..db import get_db
from ..templating import templates
from .. import calc, backup
from .presets import list_presets

router = APIRouter()


@router.get("/experiments")
def list_experiments(request: Request, q: str = "", conn: sqlite3.Connection = Depends(get_db)):
    if q:
        like = f"%{q}%"
        rows = conn.execute(
            """SELECT DISTINCT e.* FROM experiments e
               LEFT JOIN mixes m ON m.experiment_id = e.id
               LEFT JOIN mix_lines ml ON ml.mix_id = m.id
               LEFT JOIN plasmids p ON ml.plasmid_id = p.id
               WHERE e.slug LIKE ? OR e.title LIKE ? OR e.source_label LIKE ?
                  OR p.construct_id LIKE ? OR p.name LIKE ?
               ORDER BY e.experiment_date DESC, e.id DESC""",
            (like, like, like, like, like),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM experiments ORDER BY experiment_date DESC, id DESC"
        ).fetchall()
    return templates.TemplateResponse(
        "experiments_list.html", {"request": request, "experiments": rows, "q": q}
    )


@router.get("/experiments/new")
def new_experiment_form(request: Request):
    return templates.TemplateResponse(
        "experiment_form.html",
        {
            "request": request, "experiment": None,
            "default_experiment_date": datetime.date.today().isoformat(),
            "default_injection_stage": "1 cell",
            "default_incubation_at": "28°C",
        },
    )


@router.post("/experiments")
def create_experiment(
    slug: str = Form(...),
    title: str = Form(""),
    experiment_group: str = Form(""),
    repetition: str = Form(""),
    experiment_date: str = Form(""),
    injection_stage: str = Form(""),
    incubation_at: str = Form(""),
    conn: sqlite3.Connection = Depends(get_db),
):
    cur = conn.execute(
        """INSERT INTO experiments
           (slug, title, experiment_group, repetition, experiment_date,
            injection_stage, incubation_at, source)
           VALUES (?, ?, ?, ?, ?, ?, ?, 'app_created')""",
        (slug.strip(), title.strip(), experiment_group.strip(), repetition.strip(),
         experiment_date.strip() or None, injection_stage.strip(), incubation_at.strip()),
    )
    conn.commit()
    return RedirectResponse(url=f"/experiments/{cur.lastrowid}", status_code=303)


def _load_experiment_detail(conn: sqlite3.Connection, experiment_id: int):
    experiment = conn.execute("SELECT * FROM experiments WHERE id = ?", (experiment_id,)).fetchone()
    mixes = conn.execute(
        "SELECT * FROM mixes WHERE experiment_id = ? ORDER BY ordering", (experiment_id,)
    ).fetchall()
    mix_cards = []
    for mix in mixes:
        lines = conn.execute(
            """SELECT ml.*, p.name AS plasmid_name, p.construct_id AS plasmid_construct_id,
                      p.needs_review AS plasmid_needs_review
               FROM mix_lines ml
               LEFT JOIN plasmids p ON ml.plasmid_id = p.id
               WHERE ml.mix_id = ? ORDER BY ml.ordering""",
            (mix["id"],),
        ).fetchall()
        mix_cards.append((mix, calc.render_mix_rows(mix, lines)))
    return experiment, mix_cards


@router.get("/experiments/{experiment_id}")
def experiment_detail(request: Request, experiment_id: int, conn: sqlite3.Connection = Depends(get_db)):
    experiment, mix_cards = _load_experiment_detail(conn, experiment_id)
    if experiment is None:
        return RedirectResponse(url="/experiments", status_code=303)
    return templates.TemplateResponse(
        "experiment_detail.html",
        {"request": request, "experiment": experiment, "mix_cards": mix_cards,
         "presets": list_presets(conn)},
    )


@router.get("/experiments/{experiment_id}/edit")
def edit_experiment_form(request: Request, experiment_id: int, conn: sqlite3.Connection = Depends(get_db)):
    experiment = conn.execute("SELECT * FROM experiments WHERE id = ?", (experiment_id,)).fetchone()
    return templates.TemplateResponse("experiment_form.html", {"request": request, "experiment": experiment})


@router.post("/experiments/{experiment_id}/edit")
def update_experiment(
    experiment_id: int,
    slug: str = Form(...),
    title: str = Form(""),
    experiment_group: str = Form(""),
    repetition: str = Form(""),
    experiment_date: str = Form(""),
    injection_stage: str = Form(""),
    incubation_at: str = Form(""),
    conn: sqlite3.Connection = Depends(get_db),
):
    conn.execute(
        """UPDATE experiments SET slug=?, title=?, experiment_group=?, repetition=?,
           experiment_date=?, injection_stage=?, incubation_at=?, updated_at=datetime('now')
           WHERE id=?""",
        (slug.strip(), title.strip(), experiment_group.strip(), repetition.strip(),
         experiment_date.strip() or None, injection_stage.strip(), incubation_at.strip(), experiment_id),
    )
    conn.commit()
    return RedirectResponse(url=f"/experiments/{experiment_id}", status_code=303)


@router.post("/experiments/{experiment_id}/close")
def close_experiment(experiment_id: int, conn: sqlite3.Connection = Depends(get_db)):
    row = conn.execute("SELECT slug FROM experiments WHERE id = ?", (experiment_id,)).fetchone()
    if row is None:
        return RedirectResponse(url="/experiments", status_code=303)
    conn.execute(
        "UPDATE experiments SET closed_at = datetime('now'), updated_at = datetime('now') WHERE id = ?",
        (experiment_id,),
    )
    conn.commit()
    ok, message = backup.run_backup(conn, reason=f"Closed experiment '{row['slug']}'")
    return RedirectResponse(
        url=f"/experiments/{experiment_id}?backup_ok={int(ok)}&backup_msg={quote(message)}",
        status_code=303,
    )


@router.post("/experiments/{experiment_id}/reopen")
def reopen_experiment(experiment_id: int, conn: sqlite3.Connection = Depends(get_db)):
    conn.execute(
        "UPDATE experiments SET closed_at = NULL, updated_at = datetime('now') WHERE id = ?",
        (experiment_id,),
    )
    conn.commit()
    return RedirectResponse(url=f"/experiments/{experiment_id}", status_code=303)


@router.post("/experiments/{experiment_id}/delete")
def delete_experiment(experiment_id: int, conn: sqlite3.Connection = Depends(get_db)):
    conn.execute("DELETE FROM experiments WHERE id = ?", (experiment_id,))
    conn.commit()
    return RedirectResponse(url="/experiments", status_code=303)


@router.get("/experiments/{experiment_id}/export.md")
def export_markdown(experiment_id: int, conn: sqlite3.Connection = Depends(get_db)):
    experiment = conn.execute("SELECT * FROM experiments WHERE id = ?", (experiment_id,)).fetchone()
    mixes = conn.execute(
        "SELECT * FROM mixes WHERE experiment_id = ? ORDER BY ordering", (experiment_id,)
    ).fetchall()
    mixes_with_lines = []
    for mix in mixes:
        lines = conn.execute(
            """SELECT ml.*, p.name AS plasmid_name, p.construct_id AS plasmid_construct_id,
                      p.needs_review AS plasmid_needs_review
               FROM mix_lines ml
               LEFT JOIN plasmids p ON ml.plasmid_id = p.id
               WHERE ml.mix_id = ? ORDER BY ml.ordering""",
            (mix["id"],),
        ).fetchall()
        mixes_with_lines.append((mix, lines))
    markdown = calc.render_experiment_markdown(experiment, mixes_with_lines)
    slug = experiment["slug"]
    date_str = (experiment["experiment_date"] or "").replace("-", "")
    if date_str and not slug.startswith(date_str):
        filename = f"{date_str}_{slug}.md"
    else:
        filename = f"{slug}.md"
    return Response(
        content=markdown,
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
