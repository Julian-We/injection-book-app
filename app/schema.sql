-- plasmids: mirrors plasmid_db.csv + review metadata
CREATE TABLE IF NOT EXISTS plasmids (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    construct_id      TEXT NOT NULL UNIQUE,
    raw_id_original   TEXT NOT NULL,
    name              TEXT NOT NULL DEFAULT '',
    generated_by      TEXT,
    enzyme            TEXT,
    enzyme_raw        TEXT,
    needs_review      INTEGER NOT NULL DEFAULT 0,
    review_note       TEXT,
    source            TEXT NOT NULL DEFAULT 'csv_import',
    created_at        TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at        TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_plasmids_needs_review ON plasmids(needs_review);

-- experiments: one lab-book entry
CREATE TABLE IF NOT EXISTS experiments (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    slug              TEXT NOT NULL,  -- shown as "Title" in the UI
    title             TEXT,           -- shown as "Description" in the UI
    experiment_group  TEXT,
    repetition        TEXT,
    tags              TEXT NOT NULL DEFAULT '#Labbook',
    injection_stage   TEXT,
    incubation_at     TEXT,
    experiment_date   TEXT,
    source            TEXT NOT NULL DEFAULT 'app_created',
    source_label      TEXT,
    migration_note    TEXT,
    closed_at         TEXT,
    created_at        TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at        TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(slug, experiment_date)   -- same title is fine on different dates
);

-- mixes: one lettered sub-experiment (e.g. jan22a)
CREATE TABLE IF NOT EXISTS mixes (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    experiment_id     INTEGER NOT NULL REFERENCES experiments(id) ON DELETE CASCADE,
    label             TEXT NOT NULL,
    mix_volume        REAL NOT NULL DEFAULT 3,
    phr_enabled       INTEGER NOT NULL DEFAULT 1,
    phr_volume        REAL,  -- NULL = default of 10% of mix_volume
    ordering          INTEGER NOT NULL DEFAULT 0,
    created_at        TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at        TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_mixes_experiment ON mixes(experiment_id);

-- mix_lines: only user-entered lines. PhR/HEPES rows are never stored (computed live).
CREATE TABLE IF NOT EXISTS mix_lines (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    mix_id                INTEGER NOT NULL REFERENCES mixes(id) ON DELETE CASCADE,
    ordering              INTEGER NOT NULL,
    kind                  TEXT NOT NULL CHECK(kind IN ('plasmid','reagent')),
    plasmid_id            INTEGER REFERENCES plasmids(id),
    display_name_override TEXT,
    inject_amount         REAL,
    stock_conc            REAL,
    inject_volume         REAL,
    mix_volume_at_calc    REAL,
    manual_volume         REAL,
    computed_volume_cache REAL,
    computed_conc_cache   REAL,
    needs_review          INTEGER NOT NULL DEFAULT 0,
    review_note           TEXT,
    created_at            TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at            TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_mix_lines_mix ON mix_lines(mix_id);
CREATE INDEX IF NOT EXISTS idx_mix_lines_plasmid ON mix_lines(plasmid_id);
CREATE INDEX IF NOT EXISTS idx_mix_lines_needs_review ON mix_lines(needs_review);

-- presets: reusable sets of lines (e.g. a fixed base of conversion-factor RNAs)
CREATE TABLE IF NOT EXISTS presets (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    name              TEXT NOT NULL UNIQUE,
    description       TEXT,
    created_at        TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at        TEXT NOT NULL DEFAULT (datetime('now'))
);

-- preset_lines: same shape as mix_lines, copied into a mix when a preset is applied
CREATE TABLE IF NOT EXISTS preset_lines (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    preset_id             INTEGER NOT NULL REFERENCES presets(id) ON DELETE CASCADE,
    ordering              INTEGER NOT NULL,
    kind                  TEXT NOT NULL CHECK(kind IN ('plasmid','reagent')),
    plasmid_id            INTEGER REFERENCES plasmids(id),
    display_name_override TEXT,
    inject_amount         REAL,
    stock_conc            REAL,
    inject_volume         REAL,
    mix_volume_at_calc    REAL,
    manual_volume         REAL,
    created_at            TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at            TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_preset_lines_preset ON preset_lines(preset_id);
