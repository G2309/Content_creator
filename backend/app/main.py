from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import get_settings
from app.database import Base, SessionLocal, engine
from app.migrations import ensure_schema, seed_default_pains_for_existing_users
from app.routers import auth, catalogs, content, context, library, pains, scraper, users
from app.seed import seed_admin_user

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)

    ensure_schema(engine, admin_email=settings.admin_email)

    with SessionLocal() as db:
        seed_admin_user(db)
        seed_default_pains_for_existing_users(db)

    logger.info("Aplicación iniciada en entorno: %s", settings.app_env)
    yield
    logger.info("Aplicación detenida.")


app = FastAPI(
    title=settings.app_name,
    version="1.2.0",
    docs_url="/api/docs" if settings.is_development else None,
    redoc_url=None,
    openapi_url="/api/openapi.json" if settings.is_development else None,
    lifespan=lifespan,
)

if settings.cors_origins_list:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(catalogs.router)
app.include_router(pains.router)
app.include_router(content.router)
app.include_router(context.router)
app.include_router(scraper.router)
app.include_router(library.router)


@app.get("/api/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}


STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

if STATIC_DIR.exists():
    assets_dir = STATIC_DIR / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa_fallback(full_path: str):
        if full_path.startswith("api"):
            return JSONResponse({"detail": "Not Found"}, status_code=404)

        candidate = STATIC_DIR / full_path
        if full_path and candidate.is_file():
            return FileResponse(candidate)

        index = STATIC_DIR / "index.html"
        if index.exists():
            return FileResponse(index)
        return JSONResponse({"detail": "Frontend no compilado"}, status_code=404)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc: StarletteHTTPException):
    return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)
