"""Shared helpers for the two line tables, mix_lines and preset_lines.

Both tables have the same user-entered columns, so adding, editing and copying lines
works the same way for each. `table` is always one of the two literal names in
LINE_TABLES (never user input), so building the SQL with it is safe.
"""
import sqlite3

LINE_TABLES = {"mix_lines": "mix_id", "preset_lines": "preset_id"}

COPY_COLUMNS = (
    "kind", "plasmid_id", "display_name_override", "inject_amount", "stock_conc",
    "inject_volume", "mix_volume_at_calc", "manual_volume",
)


def _parent_column(table: str) -> str:
    return LINE_TABLES[table]


def next_ordering(conn: sqlite3.Connection, table: str, parent_id: int) -> int:
    parent = _parent_column(table)
    row = conn.execute(
        f"SELECT COALESCE(MAX(ordering) + 1, 0) FROM {table} WHERE {parent} = ?", (parent_id,)
    ).fetchone()
    return row[0]


def insert_plasmid_line(
    conn: sqlite3.Connection, table: str, parent_id: int, plasmid_id: int,
    inject_amount, stock_conc, inject_volume, mix_volume_at_calc,
) -> None:
    parent = _parent_column(table)
    conn.execute(
        f"""INSERT INTO {table}
            ({parent}, ordering, kind, plasmid_id, inject_amount, stock_conc, inject_volume, mix_volume_at_calc)
            VALUES (?, ?, 'plasmid', ?, ?, ?, ?, ?)""",
        (parent_id, next_ordering(conn, table, parent_id), plasmid_id,
         inject_amount, stock_conc, inject_volume, mix_volume_at_calc),
    )


def insert_reagent_line(
    conn: sqlite3.Connection, table: str, parent_id: int, display_text: str, manual_volume,
) -> None:
    parent = _parent_column(table)
    conn.execute(
        f"""INSERT INTO {table} ({parent}, ordering, kind, display_name_override, manual_volume)
            VALUES (?, ?, 'reagent', ?, ?)""",
        (parent_id, next_ordering(conn, table, parent_id), display_text.strip(), manual_volume),
    )


def update_line(
    conn: sqlite3.Connection, table: str, line_id: int, *,
    inject_amount=None, stock_conc=None, inject_volume=None, mix_volume_at_calc=None,
    display_text: str = "", manual_volume=None,
) -> None:
    """Update the editable values of a line, depending on its kind."""
    row = conn.execute(f"SELECT kind FROM {table} WHERE id = ?", (line_id,)).fetchone()
    if row is None:
        return
    if row["kind"] == "plasmid":
        conn.execute(
            f"""UPDATE {table} SET inject_amount = ?, stock_conc = ?, inject_volume = ?,
                mix_volume_at_calc = ?, updated_at = datetime('now') WHERE id = ?""",
            (inject_amount, stock_conc, inject_volume, mix_volume_at_calc, line_id),
        )
    else:
        conn.execute(
            f"""UPDATE {table} SET display_name_override = ?, manual_volume = ?,
                updated_at = datetime('now') WHERE id = ?""",
            (display_text.strip(), manual_volume, line_id),
        )


def _append_lines_to_mix(conn: sqlite3.Connection, source_lines, mix_id: int) -> int:
    """Append copies of the given line rows (values only, no review flags) to a mix."""
    start = next_ordering(conn, "mix_lines", mix_id)
    cols = ", ".join(COPY_COLUMNS)
    placeholders = ", ".join("?" for _ in COPY_COLUMNS)
    for i, line in enumerate(source_lines):
        conn.execute(
            f"INSERT INTO mix_lines (mix_id, ordering, {cols}) VALUES (?, ?, {placeholders})",
            (mix_id, start + i, *(line[c] for c in COPY_COLUMNS)),
        )
    return len(source_lines)


def copy_preset_into_mix(conn: sqlite3.Connection, preset_id: int, mix_id: int) -> int:
    """Append all of a preset's lines to a mix, as independent copies. Returns the count."""
    preset_lines = conn.execute(
        "SELECT * FROM preset_lines WHERE preset_id = ? ORDER BY ordering", (preset_id,)
    ).fetchall()
    return _append_lines_to_mix(conn, preset_lines, mix_id)


def copy_mix_lines(conn: sqlite3.Connection, src_mix_id: int, dst_mix_id: int) -> int:
    """Append copies of all of one mix's lines to another mix. Returns the count."""
    src_lines = conn.execute(
        "SELECT * FROM mix_lines WHERE mix_id = ? ORDER BY ordering", (src_mix_id,)
    ).fetchall()
    return _append_lines_to_mix(conn, src_lines, dst_mix_id)


def suggest_duplicate_label(label: str, existing_labels) -> str:
    """Suggest a label for a copy of a mix: the next free letter (jan22a -> jan22b),
    or '<label> copy' (numbered if needed) otherwise. The letter is only bumped when
    it's a single trailing letter after a digit (or the whole label), like 'jan22a'."""
    taken = {l.lower() for l in existing_labels}
    label = label.strip()
    letter_suffix = (
        len(label) >= 1 and label[-1].isascii() and label[-1].isalpha()
        and (len(label) == 1 or label[-2].isdigit())
    )
    if letter_suffix and label[-1].lower() < "z":
        base, last = label[:-1], label[-1]
        for code in range(ord(last.lower()) + 1, ord("z") + 1):
            ch = chr(code).upper() if last.isupper() else chr(code)
            if (base + ch).lower() not in taken:
                return base + ch
    candidate = f"{label} copy"
    n = 2
    while candidate.lower() in taken:
        candidate = f"{label} copy {n}"
        n += 1
    return candidate
