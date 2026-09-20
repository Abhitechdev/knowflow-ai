from datetime import datetime, timezone
from typing import Any

from app.auth import get_auth_provider
from app.core.config import settings
from app.db.session import check_database_health
from app.schemas.health import HealthResponse
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def get_health() -> HealthResponse:
    """Returns application health status, database connectivity, and auth state.
    Real probe: does not fake connection status.
    """
    db_health = await check_database_health()
    auth_status = get_auth_provider().get_status()

    # Determine overall status: healthy even if DB is unconfigured in local dev
    is_healthy = db_health["status"] in ("healthy", "unconfigured")

    return HealthResponse(
        status="healthy" if is_healthy else "degraded",
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
        database=db_health,
        auth=auth_status,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@router.get("/health/live", tags=["Health"])
async def liveness_probe() -> dict[str, str]:
    """Lightweight process liveness check.
    Returns 200 OK as long as the process is running.
    Used by container orchestrators (Kubernetes, Docker) for restart decisions.
    """
    return {"status": "alive", "timestamp": datetime.now(timezone.utc).isoformat()}


@router.get("/health/ready", tags=["Health"])
async def readiness_probe() -> JSONResponse:
    """Deep readiness probe.

    Checks:
    - Database connectivity and pgvector extension availability.
    - Auth provider configuration.
    - Application version and environment.

    Returns HTTP 200 if all checks pass, HTTP 503 if any critical check fails.
    Used by load balancers/orchestrators to determine traffic routing.
    """
    checks: dict[str, Any] = {}
    all_ready = True

    # 1. Database check
    db_health = await check_database_health()
    db_ok = db_health["status"] in ("healthy", "unconfigured")
    checks["database"] = {
        "ready": db_ok,
        "status": db_health["status"],
        "message": db_health.get("message", ""),
    }
    if not db_ok:
        all_ready = False

    # 2. Auth provider configuration check
    auth_status = get_auth_provider().get_status()
    auth_ok = auth_status.get("configured", False)
    checks["auth"] = {
        "ready": auth_ok,
        "provider": auth_status.get("provider", "unknown"),
        "configured": auth_ok,
    }
    # Auth unconfigured is only a hard failure in production
    if settings.is_production and not auth_ok:
        all_ready = False

    # 3. Environment / version info
    checks["app"] = {
        "ready": True,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
    }

    payload = {
        "ready": all_ready,
        "checks": checks,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    http_status = status.HTTP_200_OK if all_ready else status.HTTP_503_SERVICE_UNAVAILABLE
    return JSONResponse(content=payload, status_code=http_status)
