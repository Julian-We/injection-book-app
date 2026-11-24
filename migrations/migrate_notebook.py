"""Import migrations_data/notebook_data.py (the transcribed notebook recipes)
into experiments/mixes/mix_lines.

Every plasmid line's volume/concentration is computed by calling the real,
unmodified calculate_injection() live against the transcribed inputs - never
by trusting a pre-computed number - so migration exercises the exact same
code path that produced the historical recipes. The cached columns
(computed_volume_cache/computed_conc_cache) are for list-view display only;
render/export always recomputes live (see app/calc.py).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db import connection, ensure_schema, table_count  # noqa: E402
from app import injection  # noqa: E402
from migrations_data.notebook_data import EXPERIMENTS  # noqa: E402


def slugify_preview(cell_index: int, source_label: str) -> str:
    return f"preview_cell{cell_index:02d}_{source_label}"


def run(conn) -> dict:
    ensure_schema(conn)
    if table_count(conn, "experiments") > 0:
        print("experiments table is not empty - skipping import (idempotent no-op).")
        return {"skipped": True}

    n_experiments = n_mixes = n_lines = n_flagged_lines = 0
    missing_constructs: set[str] = set()

    for entry in EXPERIMENTS:
        filename = entry["filename"]
        if filename is not None:
            slug = filename
            source = "migrated_notebook_written"
        else:
            slug = slugify_preview(entry["cell_index"], entry["source_label"])
            source = "migrated_notebook_preview_only"

        migration_note = entry.get("migration_note")
        if source == "migrated_notebook_preview_only":
            preview_note = (
                "Never persisted to Obsidian in the original workflow (notebook cell only "
                "called calc_injectionmix() for a preview, not write_experiment()); migrated "
                "from the notebook cell for completeness."
            )
            migration_note = f"{migration_note}; {preview_note}" if migration_note else preview_note

        cur = conn.execute(
            """INSERT INTO experiments
               (slug, title, tags, experiment_date, source, source_label, migration_note)
               VALUES (?, NULL, '#Labbook', ?, ?, ?, ?)""",
            (slug, entry["experiment_date"], source, entry["source_label"], migration_note),
        )
        experiment_id = cur.lastrowid
        n_experiments += 1

        for mix_ordering, (mix_label, mix) in enumerate(entry["mixes"].items()):
            cur = conn.execute(
                """INSERT INTO mixes (experiment_id, label, mix_volume, phr_enabled, ordering)
                   VALUES (?, ?, 3, 1, ?)""",
                (experiment_id, mix_label, mix_ordering),
            )
            mix_id = cur.lastrowid
            n_mixes += 1

            for line_ordering, line in enumerate(mix["lines"]):
                review_note = line.get("review_note")
                needs_review = 1 if review_note else 0

                if line["kind"] == "plasmid":
                    construct_id = line["construct_id"]
                    row = conn.execute(
                        "SELECT id FROM plasmids WHERE construct_id = ?", (construct_id,)
                    ).fetchone()
                    if row is None:
                        missing_constructs.add(construct_id)
                        plasmid_id = None
                        note = f"Construct ID '{construct_id}' not found in plasmids table"
                        review_note = f"{review_note}; {note}" if review_note else note
                        needs_review = 1
                    else:
                        plasmid_id = row["id"]

                    inject_amount = line["inject_amount"]
                    stock_conc = line["stock_conc"]
                    inject_volume = line.get("inject_volume", 2)
                    mix_volume_at_calc = line.get("mix_volume_at_calc", 3)
                    vol, conc, _ = injection.calculate_injection(
                        inject_amount, stock_conc, inject_volume, mix_volume_at_calc
                    )
                    conn.execute(
                        """INSERT INTO mix_lines
                           (mix_id, ordering, kind, plasmid_id, display_name_override,
                            inject_amount, stock_conc, inject_volume, mix_volume_at_calc,
                            computed_volume_cache, computed_conc_cache, needs_review, review_note)
                           VALUES (?, ?, 'plasmid', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        (mix_id, line_ordering, plasmid_id, line["display_text"],
                         inject_amount, stock_conc, inject_volume, mix_volume_at_calc,
                         round(vol, 3), conc, needs_review, review_note),
                    )
                else:
                    conn.execute(
                        """INSERT INTO mix_lines
                           (mix_id, ordering, kind, display_name_override, manual_volume,
                            computed_volume_cache, needs_review, review_note)
                           VALUES (?, ?, 'reagent', ?, ?, ?, ?, ?)""",
                        (mix_id, line_ordering, line["display_text"], line["manual_volume"],
                         line["manual_volume"], needs_review, review_note),
                    )
                n_lines += 1
                if needs_review:
                    n_flagged_lines += 1

    conn.commit()

    if missing_constructs:
        raise AssertionError(
            f"{len(missing_constructs)} construct ID(s) referenced by notebook recipes were not "
            f"found in the plasmids table (import plasmids first): {sorted(missing_constructs)}"
        )

    print(
        f"Imported {n_experiments} experiments, {n_mixes} mixes, {n_lines} lines "
        f"({n_flagged_lines} lines flagged for review)."
    )
    return {
        "skipped": False, "experiments": n_experiments, "mixes": n_mixes,
        "lines": n_lines, "flagged": n_flagged_lines,
    }


if __name__ == "__main__":
    with connection() as conn:
        run(conn)
