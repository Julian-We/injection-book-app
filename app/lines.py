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


def copy_preset_into_mix(conn: sqlite3.Connection, preset_id: int, mix_id: int) -> int:
    """Append all of a preset's lines to a mix, as independent copies. Returns the count."""
    preset_lines = conn.execute(
        "SELECT * FROM preset_lines WHERE preset_id = ? ORDER BY ordering", (preset_id,)
    ).fetchall()
    start = next_ordering(conn, "mix_lines", mix_id)
    cols = ", ".join(COPY_COLUMNS)
    placeholders = ", ".join("?" for _ in COPY_COLUMNS)
    for i, line in enumerate(preset_lines):
        conn.execute(
            f"INSERT INTO mix_lines (mix_id, ordering, {cols}) VALUES (?, ?, {placeholders})",
            (mix_id, start + i, *(line[c] for c in COPY_COLUMNS)),
        )
    return len(preset_lines)
