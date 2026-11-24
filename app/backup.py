"""Back up the live SQLite database to a dedicated GitHub repo.

Triggered as a side effect of closing an experiment (see app/routes/experiments.py).
Dumps the DB as SQL text (git-diffable, unlike a raw binary copy) into a git
working tree persisted at BACKUP_DIR, then commits and pushes it. Failure here
must never block the caller from closing the experiment - every git/network
error is caught and returned as a (False, message) result instead of raised.
"""
import os
import sqlite3
import subprocess
from pathlib import Path

BACKUP_DIR = Path(os.environ.get("BACKUP_DIR", "/backup"))
DUMP_FILENAME = "injection_db_dump.sql"


def _run(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        args, cwd=str(cwd), capture_output=True, text=True, timeout=60, check=True,
    )


def _remote_url(repo: str, token: str) -> str:
    # repo may be given as "owner/repo" or a full https://github.com/... URL.
    if repo.startswith("http://") or repo.startswith("https://"):
        rest = repo.split("github.com/", 1)[-1]
    else:
        rest = repo
    rest = rest.removesuffix(".git")
    return f"https://x-access-token:{token}@github.com/{rest}.git"


def _ensure_checked_out(branch: str) -> None:
    """Get the working tree onto `branch`, creating it if it doesn't exist yet.

    Handles: a genuinely empty remote repo (unborn HEAD), a remote whose
    default branch has a different name than `branch` (e.g. master vs main),
    and a leftover broken state from a previous failed clone attempt (also
    an unborn HEAD) - all without touching/deleting anything already on the
    remote.
    """
    head_ok = subprocess.run(
        ["git", "rev-parse", "--verify", "HEAD"], cwd=str(BACKUP_DIR),
        capture_output=True, text=True,
    ).returncode == 0

    if not head_ok:
        _run(["git", "checkout", "--orphan", branch], cwd=BACKUP_DIR)
        subprocess.run(["git", "reset", "--hard"], cwd=str(BACKUP_DIR), capture_output=True, text=True)
        return

    checkout = subprocess.run(
        ["git", "checkout", branch], cwd=str(BACKUP_DIR), capture_output=True, text=True,
    )
    if checkout.returncode != 0:
        _run(["git", "checkout", "-b", branch], cwd=BACKUP_DIR)
    else:
        subprocess.run(  # best-effort - e.g. no upstream tracking yet is fine
            ["git", "pull", "--ff-only", "origin", branch], cwd=str(BACKUP_DIR),
            capture_output=True, text=True,
        )


def run_backup(conn: sqlite3.Connection, reason: str) -> tuple[bool, str]:
    repo = os.environ.get("GITHUB_BACKUP_REPO", "").strip()
    token = os.environ.get("GITHUB_BACKUP_TOKEN", "").strip()
    branch = os.environ.get("GITHUB_BACKUP_BRANCH", "main").strip() or "main"

    if not repo or not token:
        return False, "Backup not configured (GITHUB_BACKUP_REPO / GITHUB_BACKUP_TOKEN not set)."

    url = _remote_url(repo, token)
    try:
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        if not (BACKUP_DIR / ".git").exists():
            _run(["git", "clone", url, "."], cwd=BACKUP_DIR)
        else:
            _run(["git", "remote", "set-url", "origin", url], cwd=BACKUP_DIR)
            _run(["git", "fetch", "origin"], cwd=BACKUP_DIR)

        _ensure_checked_out(branch)

        dump_path = BACKUP_DIR / DUMP_FILENAME
        with open(dump_path, "w", encoding="utf-8") as f:
            for line in conn.iterdump():
                f.write(f"{line}\n")

        _run(["git", "add", "-A"], cwd=BACKUP_DIR)
        commit = subprocess.run(
            ["git", "commit", "-m", reason], cwd=str(BACKUP_DIR),
            capture_output=True, text=True, timeout=60,
        )
        if commit.returncode != 0 and "nothing to commit" not in commit.stdout:
            raise RuntimeError(f"git commit failed: {commit.stdout}\n{commit.stderr}")

        _run(["git", "push", "-u", "origin", branch], cwd=BACKUP_DIR)
    except subprocess.CalledProcessError as e:
        return False, f"Backup failed: {e.stderr.strip() or e.stdout.strip() or e}"
    except Exception as e:  # noqa: BLE001 - any failure here is reported, never raised
        return False, f"Backup failed: {e}"

    return True, f"Backed up to {repo}@{branch}"
