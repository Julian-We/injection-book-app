"""Live rendering of a mix's lines using the original injection.py calculation logic.

PhR and HEPES rows are never persisted in the database (see schema.sql) - they are
always derived here from the mix's stored lines, by rebuilding the same dict shape
that calc_injectionmix() expects and calling it directly, so the web UI can never
drift from the historical calculation code.
"""
import sqlite3
from dataclasses import dataclass

from . import injection


@dataclass
class RenderedLine:
    ordering: int
    kind: str
    label: str
    volume_ul: float
    conc_ng_per_ul: float | None
    amount_pg: float | str
    needs_review: bool
    review_note: str | None
    id: int | None = None
    construct_id: str | None = None
    # Raw stored values, used to pre-fill the edit form (None for PhR/HEPES rows)
    inject_amount: float | None = None
    stock_conc: float | None = None
    inject_volume: float | None = None
    mix_volume_at_calc: float | None = None
    manual_volume: float | None = None


def line_label(row: sqlite3.Row) -> str:
    """Name text for the markdown dict key - must keep embedding '| construct_id'
    for un-overridden plasmid lines, since calc_injectionmix's markdown table
    relies on that literal '|' to populate its "Construct Number" column."""
    if row["display_name_override"]:
        return row["display_name_override"]
    if row["kind"] == "plasmid" and row["plasmid_name"]:
        return f'{row["plasmid_name"]} | {row["plasmid_construct_id"]}'
    if row["kind"] == "plasmid":
        return row["plasmid_construct_id"] or "(unknown construct)"
    return "(unnamed reagent)"


def html_display_name(row: sqlite3.Row) -> str:
    """Name text for the HTML 'Name' column, which has its own Construct ID
    column - so un-overridden plasmid lines show just the plasmid name."""
    if row["display_name_override"]:
        return row["display_name_override"]
    if row["kind"] == "plasmid":
        return row["plasmid_name"] or row["plasmid_construct_id"] or "(unknown construct)"
    return "(unnamed reagent)"


def phr_volume(mix) -> float:
    """PhR volume [µL] for a mix: its own setting, or the historical 10% default."""
    keys = mix.keys() if hasattr(mix, "keys") else ()
    if "phr_volume" in keys and mix["phr_volume"] is not None:
        return float(mix["phr_volume"])
    return mix["mix_volume"] * 0.1


def build_dict_for_mix(lines: list[sqlite3.Row]) -> dict:
    """Rebuild the {label: value} dict shape calc_injectionmix() expects."""
    dic = {}
    for row in lines:
        label = line_label(row)
        # Disambiguate duplicate labels (calc_injectionmix uses a dict, so keys must be unique)
        base_label = label
        suffix = 1
        while label in dic:
            suffix += 1
            label = f"{base_label} ({suffix})"
        if row["kind"] == "plasmid":
            dic[label] = injection.calculate_injection(
                row["inject_amount"],
                row["stock_conc"],
                row["inject_volume"] or 2,
                row["mix_volume_at_calc"] or 3,
            )
        else:
            dic[label] = float(row["manual_volume"])
    return dic


def render_mix_table(mix: sqlite3.Row, lines: list[sqlite3.Row]) -> str:
    """Return the markdown table for a mix, computed live (matches calc_injectionmix)."""
    dic = build_dict_for_mix(lines)
    return injection.calc_injectionmix(
        dic, mix_vol=mix["mix_volume"], phr=bool(mix["phr_enabled"]), phr_vol=phr_volume(mix)
    )


def render_mix_rows(mix: sqlite3.Row, lines: list[sqlite3.Row]) -> list[RenderedLine]:
    """Structured (non-markdown) rows for the HTML UI, including live PhR/HEPES rows."""
    rendered: list[RenderedLine] = []
    total_vol = 0.0
    for row in lines:
        label = html_display_name(row)
        construct_id = row["plasmid_construct_id"] if row["kind"] == "plasmid" else None
        if row["kind"] == "plasmid":
            vol, conc, amount = injection.calculate_injection(
                row["inject_amount"],
                row["stock_conc"],
                row["inject_volume"] or 2,
                row["mix_volume_at_calc"] or 3,
            )
        else:
            vol, conc, amount = float(row["manual_volume"]), None, "xx"
        total_vol += vol
        rendered.append(
            RenderedLine(
                ordering=row["ordering"],
                kind=row["kind"],
                label=label,
                volume_ul=round(vol, 3),
                conc_ng_per_ul=conc,
                amount_pg=amount,
                needs_review=bool(row["needs_review"]),
                review_note=row["review_note"],
                id=row["id"],
                construct_id=construct_id,
                inject_amount=row["inject_amount"],
                stock_conc=row["stock_conc"],
                inject_volume=row["inject_volume"],
                mix_volume_at_calc=row["mix_volume_at_calc"],
                manual_volume=row["manual_volume"],
            )
        )
    mix_vol = mix["mix_volume"]
    if mix["phr_enabled"]:
        phr_vol = round(phr_volume(mix), 3)
        total_vol += phr_vol
        rendered.append(
            RenderedLine(
                ordering=10_000, kind="phr", label="PhR",
                volume_ul=phr_vol, conc_ng_per_ul=None, amount_pg="-",
                needs_review=False, review_note=None,
            )
        )
    hepes_vol = round(mix_vol - total_vol, 3)
    rendered.append(
        RenderedLine(
            ordering=10_001, kind="hepes", label="HEPES",
            volume_ul=hepes_vol, conc_ng_per_ul=None, amount_pg="-",
            needs_review=False, review_note=None,
        )
    )
    return rendered


MARKDOWN_PREAMBLE = """---
Experiment_group: {experiment_group}
Repetition: {repetition}
---
Tags: {tags}
# Aim of experiment
{title}
***

# Injection

"""

MARKDOWN_EPILOG = """**Injection stage:** {injection_stage}
**Incubation at:** {incubation_at}
"""


def render_experiment_markdown(
    experiment: sqlite3.Row, mixes_with_lines: list[tuple[sqlite3.Row, list[sqlite3.Row]]]
) -> str:
    """Reproduce write_experiment()'s original file format for export/download."""
    parts = [
        MARKDOWN_PREAMBLE.format(
            experiment_group=experiment["experiment_group"] or "",
            repetition=experiment["repetition"] or "",
            tags=experiment["tags"] or "#Labbook",
            title=experiment["title"] or "Lorem ipsum",
        )
    ]
    for mix, lines in mixes_with_lines:
        parts.append(f"## {mix['label']}\n\n")
        parts.append(render_mix_table(mix, lines))
        parts.append("\n")
    parts.append(
        MARKDOWN_EPILOG.format(
            injection_stage=experiment["injection_stage"] or "# cell stage",
            incubation_at=experiment["incubation_at"] or "## ºC",
        )
    )
    parts.append("***\n")
    return "".join(parts)
