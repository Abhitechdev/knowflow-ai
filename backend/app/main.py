import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.core.security_headers import SecurityHeadersMiddleware
from app.core.sentry import init_sentry
from app.db.session import check_database_health

logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("knowflow")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION} [{settings.ENVIRONMENT}]")

    # Initialize Sentry in production (no-op if SENTRY_DSN is empty)
    init_sentry(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
        release=settings.VERSION,
    )

    db_status = await check_database_health()
    logger.info(f"Database status on startup: {db_status['status']} - {db_status['message']}")

    if settings.is_production:
        logger.info("Production mode: fail-closed authentication is ACTIVE.")
        logger.info(f"CORS allowlist: {settings.CORS_ORIGINS}")

    yield
    logger.info("Shutting down KnowFlow AI backend.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Enterprise Knowledge & SOP Agent backend API",
    lifespan=lifespan,
    # Disable interactive docs in production to reduce attack surface
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# ------------------------------------------------------------------ #
# Security Headers — production hardening                             #
# ------------------------------------------------------------------ #
if settings.is_production:
    app.add_middleware(SecurityHeadersMiddleware)

# ------------------------------------------------------------------ #
# CORS — explicit origin allowlist, no wildcards                      #
# ------------------------------------------------------------------ #
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "X-Workspace-ID"],
)

# Mount API endpoints
app.include_router(api_router, prefix="/api")


@app.get("/", tags=["Root"])
async def root():
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "health": "/api/health",
        "docs": "/docs" if settings.DEBUG else "disabled",
    }
