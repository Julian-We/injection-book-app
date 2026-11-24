import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from . import db
from .routes import experiments, mixes, plasmids

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from migrations import migrate_plasmids, migrate_notebook  # noqa: E402


@asynccontextmanager
async def lifespan(app: FastAPI):
    conn = db.get_connection()
    try:
        db.ensure_schema(conn)
        migrate_plasmids.run(conn)
        migrate_notebook.run(conn)
    finally:
        conn.close()
    yield


app = FastAPI(title="Injection Recipes", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(Path(__file__).parent / "static")), name="static")
app.include_router(experiments.router)
app.include_router(mixes.router)
app.include_router(plasmids.router)


@app.get("/")
def root():
    return RedirectResponse(url="/experiments")
