# Injection Recipes

A small web app that replaces the `2025_injection.ipynb` workflow for building
zebrafish microinjection mix recipes. Construct data is looked up automatically
from a migrated `plasmid_db.csv`; all recipes are stored in a SQLite database
instead of one-off markdown files.

## Run it

```bash
docker compose up -d
```

Then open `http://<host>:8000`. On first startup the container automatically:

1. Creates the SQLite schema at `/data/injection.db` (persisted in the
   `injection_data` named volume).
2. Imports all 6,478 rows of `migrations_data/plasmid_db.csv` into the
   `plasmids` table (idempotent - only runs if the table is empty).
3. Imports all ~90 historical recipes transcribed from the original notebook
   into `experiments`/`mixes`/`mix_lines` (idempotent - only runs if the
   `experiments` table is empty).

Restarting the container is always safe - the migrations are no-ops once data
exists.

No authentication is included; the app binds to `0.0.0.0:8000` by design
(single user, network access controlled by you - e.g. firewall/VPN/SSH tunnel).

## Using it

- **Experiments** - a "lab-book entry" for one day's injections (was one
  Obsidian `.md` file).
- **Mixes** - a lettered sub-experiment (e.g. `jan22a`), belonging to an
  experiment.
- **Lines** - either a plasmid/RNA construct (enter the construct ID + amount
  [pg] + stock conc [ng/µL] - the name is looked up automatically; if the ID
  isn't in the database yet you'll be prompted to add it) or a
  morpholino/reagent (free-text label + manual volume in µL).
  Construct IDs are matched case-insensitively (`f126` finds `F126`). Use the
  ✎ button on a line to edit its amount/concentration (or label/volume).
- **Presets** (nav link) - reusable sets of lines, e.g. a fixed base of
  conversion-factor RNAs. Pick one when adding a mix, or use "Apply preset" on
  an existing mix, and its lines are copied in. The copies are ordinary mix
  lines, so editing them never changes the preset (and editing/deleting the
  preset never changes existing mixes).
- PhR and HEPES top-up rows are always computed live from the mix's other
  lines - they are never stored, so editing a mix's volume/PhR setting is
  always reflected correctly.
- **Export as Markdown** on an experiment page reproduces the original
  `write_experiment()` file format, for pasting into Obsidian or elsewhere.
- **Flagged plasmids** (nav link) lists every plasmid or recipe line migrated
  with an unresolved data-quality note (e.g. a garbled ID, a name mismatch) -
  review and clear them at your own pace; nothing is silently altered.
- **Close experiment** marks it closed (just a label, not read-only) and
  triggers a GitHub backup of the whole database - see below to set that up.

## Backing up the database to GitHub

Whenever an experiment is closed, the app dumps the whole SQLite database as
SQL text and pushes it as a commit to a private GitHub repo you control. Setup
is a one-time, manual step (only you can create the repo/token):

1. Create a new **private** GitHub repo (e.g. `injection-db-backup`) - it's
   fine to leave it completely empty, the app creates the configured branch
   itself on the first backup either way.
2. Generate a GitHub **personal access token** with write access scoped to
   just that repo (Settings → Developer settings → Fine-grained tokens →
   this repository only → Contents: Read and write).
3. Copy `.env.example` to `.env` in this directory and fill in
   `GITHUB_BACKUP_REPO` (e.g. `yourname/injection-db-backup`),
   `GITHUB_BACKUP_TOKEN`, and `GITHUB_BACKUP_BRANCH` (default `main`).
   `.env` is gitignored - it never gets committed or baked into the image.
4. `docker compose up -d --build` to pick up the new environment variables.

If a backup ever gets stuck in a way that doesn't resolve itself on the next
close, the fallback is to wipe the working copy and let it re-clone fresh:
`docker compose down && docker volume rm injection_app_backup_repo && docker compose up -d`.

Closing an experiment now pushes a commit containing `injection_db_dump.sql`
(the full DB as SQL - diffable in GitHub, unlike a binary file) to that repo.
If `.env` isn't set up yet, closing still works, but the banner on the
experiment page will say the backup isn't configured instead of erroring.

Note: the token ends up stored in the backup working tree's git config inside
the `backup_repo` Docker volume, so use a token scoped to only this one repo.

## Development

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
DATABASE_PATH=./dev.db uvicorn app.main:app --reload
pytest tests/
```

## Re-running migrations manually

```bash
docker compose exec web python -m migrations.migrate_plasmids
docker compose exec web python -m migrations.migrate_notebook
```

(Both are no-ops if their target table already has rows - wipe the volume to
force a clean re-import.)
