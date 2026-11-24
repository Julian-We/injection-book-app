"""Import migrations_data/plasmid_db.csv into the plasmids table.

Normalization policy (see plan file for full rationale):
  - Always-safe: strip surrounding whitespace/vertical-tabs from ID and Name
    (Python's str.strip() already treats \\x0b as whitespace, confirmed).
  - Flag, never silently transform, anything else unusual in the ID field:
    mid-string control characters, a literal '?' (garbled ID), an embedded
    space (ID absorbed Name text - the known E855/E884 cases), a lowercase
    first letter (e958/e964), or a trailing period.
  - C755-1 / C755-2 are legitimate distinct rows sharing a base number with a
    "-1"/"-2" suffix - intentionally NOT flagged. Do not "deduplicate" these.
  - Empty Name is common for reserved/placeholder IDs (8 rows) - recorded
    with an informational note but needs_review stays 0 (not a cleanup item).
  - Enzyme field: mid-string vertical-tabs are cosmetic (Excel Alt+Enter
    artifacts) - replaced with "; " for display only; enzyme_raw keeps the
    untouched original.
"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db import connection, ensure_schema, table_count  # noqa: E402

CSV_PATH = Path(__file__).resolve().parent.parent / "migrations_data" / "plasmid_db.csv"


def normalize_row(raw_id: str, raw_name: str, raw_generated_by: str, raw_enzyme: str):
    construct_id = raw_id.strip()
    name = raw_name.strip()
    generated_by = (raw_generated_by or "").strip()
    enzyme_raw = raw_enzyme or ""
    enzyme = enzyme_raw.strip().replace("\x0b", "; ")

    reasons = []
    if any(ch in construct_id for ch in ("\x0b", "\t", "\n", "\r")):
        reasons.append("embedded control character in ID field")
    if "?" in construct_id:
        reasons.append("garbled ID (contains '?'); correct ID unknown, verify against original spreadsheet")
    if " " in construct_id:
        reasons.append("ID field contains a space - likely absorbed Name text or other corruption")
    if construct_id[:1].islower():
        reasons.append("lowercase first letter, inconsistent with the uppercase-prefix convention")
    if construct_id.endswith("."):
        reasons.append("trailing period in ID")

    needs_review = 1 if reasons else 0
    review_note = "; ".join(reasons) if reasons else None

    if name == "":
        note = "Reserved/placeholder ID with no assigned name in source CSV"
        review_note = f"{review_note}; {note}" if review_note else note

    return {
        "construct_id": construct_id,
        "raw_id_original": raw_id,
        "name": name,
        "generated_by": generated_by,
        "enzyme": enzyme,
        "enzyme_raw": enzyme_raw,
        "needs_review": needs_review,
        "review_note": review_note,
    }


def run(conn) -> dict:
    ensure_schema(conn)
    if table_count(conn, "plasmids") > 0:
        print("plasmids table is not empty - skipping import (idempotent no-op).")
        return {"skipped": True}

    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    seen_ids: dict[str, int] = {}
    inserted = 0
    flagged = 0
    for raw in rows:
        rec = normalize_row(raw["ID"], raw["Name"], raw.get("generated_by", ""), raw.get("Enzyme", ""))
        cid = rec["construct_id"]
        if cid in seen_ids:
            seen_ids[cid] += 1
            dup_note = f"Duplicate normalized construct_id (occurrence #{seen_ids[cid]}) - suffixed to stay unique"
            rec["construct_id"] = f"{cid}__dup{seen_ids[cid]}"
            rec["needs_review"] = 1
            rec["review_note"] = f"{rec['review_note']}; {dup_note}" if rec["review_note"] else dup_note
        else:
            seen_ids[cid] = 1

        conn.execute(
            """INSERT INTO plasmids
               (construct_id, raw_id_original, name, generated_by, enzyme, enzyme_raw,
                needs_review, review_note, source)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'csv_import')""",
            (
                rec["construct_id"], rec["raw_id_original"], rec["name"], rec["generated_by"],
                rec["enzyme"], rec["enzyme_raw"], rec["needs_review"], rec["review_note"],
            ),
        )
        inserted += 1
        if rec["needs_review"]:
            flagged += 1

    conn.commit()

    source_row_count = len(rows)
    assert inserted == source_row_count, (
        f"Row count mismatch: read {source_row_count} rows from CSV but inserted {inserted} - "
        "migration must not silently drop or merge rows."
    )
    print(f"Imported {inserted} plasmids ({flagged} flagged for review).")
    return {"skipped": False, "inserted": inserted, "flagged": flagged}


if __name__ == "__main__":
    with connection() as conn:
        run(conn)
