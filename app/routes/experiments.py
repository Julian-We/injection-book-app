import datetime
import sqlite3

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse, Response

from urllib.parse import quote

from ..db import get_db
from ..templating import templates
from .. import calc, backup, lines as line_utils
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


def _experiment_form_values(**fields) -> dict:
    return {k: v.strip() for k, v in fields.items()}


DUPLICATE_TITLE_ERROR = (
    "An experiment with this title already exists on this date. "
    "Use a different title (e.g. add \"repeat 2\") or a different date."
)


def _form_error(request: Request, values: dict, experiment_id: int | None = None):
    """Re-render the experiment form with the entered values and an error banner."""
    experiment = dict(values, id=experiment_id) if experiment_id is not None else None
    return templates.TemplateResponse(
        "experiment_form.html",
        {"request": request, "experiment": experiment, "values": values, "error": DUPLICATE_TITLE_ERROR},
        status_code=400,
    )


@router.post("/experiments")
def create_experiment(
    request: Request,
    slug: str = Form(...),
    title: str = Form(""),
    experiment_group: str = Form(""),
    repetition: str = Form(""),
    experiment_date: str = Form(""),
    injection_stage: str = Form(""),
    incubation_at: str = Form(""),
    conn: sqlite3.Connection = Depends(get_db),
):
    v = _experiment_form_values(
        slug=slug, title=title, experiment_group=experiment_group, repetition=repetition,
        experiment_date=experiment_date, injection_stage=injection_stage, incubation_at=incubation_at,
    )
    try:
        cur = conn.execute(
            """INSERT INTO experiments
               (slug, title, experiment_group, repetition, experiment_date,
                injection_stage, incubation_at, source)
               VALUES (?, ?, ?, ?, ?, ?, ?, 'app_created')""",
            (v["slug"], v["title"], v["experiment_group"], v["repetition"],
             v["experiment_date"] or None, v["injection_stage"], v["incubation_at"]),
        )
    except sqlite3.IntegrityError:
        return _form_error(request, v)
    conn.commit()
    return RedirectResponse(url=f"/experiments/{cur.lastrowid}", status_code=303)


def _load_experiment_detail(conn: sqlite3.Connection, experiment_id: int):
    experiment = conn.execute("SELECT * FROM experiments WHERE id = ?", (experiment_id,)).fetchone()
    mixes = conn.execute(
        "SELECT * FROM mixes WHERE experiment_id = ? ORDER BY ordering", (experiment_id,)
    ).fetchall()
    mix_cards = []
    labels = [m["label"] for m in mixes]
    for mix in mixes:
        lines = conn.execute(
            """SELECT ml.*, p.name AS plasmid_name, p.construct_id AS plasmid_construct_id,
                      p.needs_review AS plasmid_needs_review
               FROM mix_lines ml
               LEFT JOIN plasmids p ON ml.plasmid_id = p.id
               WHERE ml.mix_id = ? ORDER BY ml.ordering""",
            (mix["id"],),
        ).fetchall()
        suggested = line_utils.suggest_duplicate_label(mix["label"], labels)
        mix_cards.append((mix, calc.render_mix_rows(mix, lines), suggested))
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
    request: Request,
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
    v = _experiment_form_values(
        slug=slug, title=title, experiment_group=experiment_group, repetition=repetition,
        experiment_date=experiment_date, injection_stage=injection_stage, incubation_at=incubation_at,
    )
    try:
        conn.execute(
            """UPDATE experiments SET slug=?, title=?, experiment_group=?, repetition=?,
               experiment_date=?, injection_stage=?, incubation_at=?, updated_at=datetime('now')
               WHERE id=?""",
            (v["slug"], v["title"], v["experiment_group"], v["repetition"],
             v["experiment_date"] or None, v["injection_stage"], v["incubation_at"], experiment_id),
        )
    except sqlite3.IntegrityError:
        return _form_error(request, v, experiment_id)
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
    return Response(
        content=markdown,
        media_type="text/markdown",
        headers={"Content-Disposition": _content_disposition(export_filename(experiment))},
    )


def export_filename(experiment) -> str:
    """'<YYYYMMDD> <title>.md', e.g. '20261006 heatshock timelapse test.md'.
    Titles that already start with the date (historical ones) aren't prefixed again."""
    title = experiment["slug"].strip()
    date_str = (experiment["experiment_date"] or "").replace("-", "")
    name = f"{date_str} {title}" if date_str and not title.startswith(date_str) else title
    for ch in '/\\"':
        name = name.replace(ch, "-")
    return f"{name}.md"


def _content_disposition(filename: str) -> str:
    """HTTP headers must be Latin-1, so non-ASCII names (e.g. an en dash) go in the
    RFC 5987 filename* parameter, with an ASCII-only fallback for old clients."""
    ascii_fallback = filename.encode("ascii", "replace").decode("ascii").replace("?", "_")
    return f"attachment; filename=\"{ascii_fallback}\"; filename*=UTF-8''{quote(filename)}"
