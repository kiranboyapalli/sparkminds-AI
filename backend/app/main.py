"""
SparkMinds AI — FastAPI Main Application Entry Point (Production & Development Ready)
"""
import logging
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from app.core.config import settings, SUPPORTED_LANGUAGES
from app.core.email_provider import (
    get_email_service_health_summary,
    probe_email_network_connectivity,
)
from app.core.repository import repo
from app.routers.api_router import router as api_router
from app.routers.ecosystem_router import ecosystem_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] SparkMinds-AI: %(message)s",
)
logger = logging.getLogger("sparkminds")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=f"{settings.TAGLINE} — {settings.POSITIONING}",
    version=settings.VERSION,
)

allowed_origins = list(dict.fromkeys([settings.FRONTEND_ORIGIN, *settings.CORS_ORIGINS]))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if "*" not in allowed_origins else ["*"],
    allow_origin_regex=r"https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def auth_cookie_header_bridge(request: Request, call_next):
    """
    Seamlessly bridges HttpOnly `sparkminds_access_token` cookie into request headers
    for all `/api/*` endpoints when no explicit Authorization or X-SparkMinds-Token
    header is provided. Explicit headers always take precedence for mobile/API clients.
    """
    if request.url.path.startswith("/api/"):
        cookie_token = (request.cookies.get("sparkminds_access_token") or "").strip()
        if cookie_token:
            raw_headers = list(request.scope.get("headers") or [])
            has_auth_hdr = any(
                k.lower() in (b"authorization", b"x-sparkminds-token")
                for k, _ in raw_headers
            )
            if not has_auth_hdr:
                raw_headers.append((b"x-sparkminds-token", cookie_token.encode("latin-1")))
                request.scope["headers"] = raw_headers
    return await call_next(request)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled error on %s %s: %s", request.method, request.url.path, exc)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An unexpected server error occurred. Your academic records remain safely stored.",
            "error_type": type(exc).__name__,
        },
    )


app.include_router(api_router)
app.include_router(ecosystem_router)


@app.on_event("startup")
def _log_email_network_diagnostics() -> None:
    """Logs non-sensitive outbound email transport diagnostics on startup."""
    if settings.ENV.strip().lower() == "production":
        try:
            probe = probe_email_network_connectivity()
            summary = get_email_service_health_summary(include_probe=False)
            logger.info(
                "Email transport diagnostics: active_provider=%s https_api_configured=%s "
                "smtp_587_v4=%s smtp_587_v6=%s smtp_465_v4=%s smtp_465_v6=%s "
                "brevo_443=%s resend_443=%s",
                summary["active_provider"],
                summary["https_api_configured"],
                probe["smtp_gmail_587_ipv4"],
                probe["smtp_gmail_587_ipv6"],
                probe["smtp_gmail_465_ipv4"],
                probe["smtp_gmail_465_ipv6"],
                probe["brevo_https_443_ipv4"],
                probe["resend_https_443_ipv4"],
            )
        except Exception as exc:
            logger.warning("Email connectivity diagnostic skipped: %s", type(exc).__name__)


@app.get("/api/health")
def health_check():
    """Health check endpoint verifying backend, production database & full multi-agent readiness."""
    pg_health = repo.pg.health_summary()
    pg_connected = bool(pg_health.get("postgresql_connected"))
    is_prod = settings.ENV.strip().lower() == "production"
    return {
        "status": "ok",
        "product": settings.PROJECT_NAME,
        "tagline": settings.TAGLINE,
        "positioning": settings.POSITIONING,
        "version": settings.VERSION,
        "environment": settings.ENV,
        "database": {
            "engine": (
                "PostgreSQL (Managed Persistent Production DB) + SQLite Local Cache"
                if pg_connected
                else "SQLite WAL + JSON Snapshot Dual Persistence"
            ),
            "persistent_storage": pg_connected,
            "postgresql_configured": bool(pg_health.get("postgresql_configured")),
            "postgresql_connected": pg_connected,
            "db_user_accounts_count": pg_health.get("db_user_accounts_count"),
            "db_active_sessions_count": pg_health.get("db_active_sessions_count"),
            "sqlite_ready": repo.sqlite_db_path.exists(),
            "json_ready": repo.db_file.exists(),
            "registered_students_count": len(repo.students),
            "backups_directory_ready": repo.backups_dir.exists(),
            "uploads_directory_ready": repo.uploads_dir.exists(),
        },
        "email_service": get_email_service_health_summary(include_probe=is_prod),
        "supported_languages_count": len(SUPPORTED_LANGUAGES),
        "tier1_priority_languages": [
            lang["name"] for lang in SUPPORTED_LANGUAGES if lang["tier"] == 1
        ],
        "agents_configured": [
            {"id": "discovery", "name": "Discovery Agent", "icon": "Compass"},
            {"id": "intelligence", "name": "Intelligence Agent", "icon": "Brain"},
            {"id": "strategy", "name": "Strategy Agent", "icon": "Target"},
            {"id": "growth", "name": "Growth Agent", "icon": "TrendingUp"},
        ],
    }


@app.get("/api/meta/languages")
def list_supported_languages():
    """Returns English + all 22 Eighth-Schedule Indian languages with verification status."""
    return {
        "total": len(SUPPORTED_LANGUAGES),
        "languages": SUPPORTED_LANGUAGES,
    }


# Serve compiled Frontend PWA (frontend/dist) when present for unified single-container/cloud production hosting
FRONTEND_DIST_DIR = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if FRONTEND_DIST_DIR.exists() and (FRONTEND_DIST_DIR / "index.html").exists():
    assets_dir = FRONTEND_DIST_DIR / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_pwa_frontend(full_path: str):
        if full_path.startswith("api/"):
            return JSONResponse(status_code=404, content={"detail": "API endpoint not found"})
        candidate = (FRONTEND_DIST_DIR / full_path).resolve()
        no_cache_headers = {
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        }
        if (
            full_path
            and str(candidate).startswith(str(FRONTEND_DIST_DIR.resolve()))
            and candidate.is_file()
        ):
            # For sw.js and manifest.json, never cache
            if candidate.name in ["sw.js", "manifest.json", "index.html"]:
                return FileResponse(str(candidate), headers=no_cache_headers)
            return FileResponse(str(candidate))
        # Default fallback is index.html with strict no-cache headers
        return FileResponse(str(FRONTEND_DIST_DIR / "index.html"), headers=no_cache_headers)


