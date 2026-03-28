import logging
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.api import api_router
from app.config import settings
from app.middleware.audit_log import AuditLogMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.shared.exceptions import APIErrorResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_START_TIME = time.monotonic()

app = FastAPI(title="TakiOS API", version=settings.app_version)

cors_origins = [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "X-Request-Id"],
)
app.add_middleware(AuditLogMiddleware)
app.add_middleware(RateLimitMiddleware)


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-Id"] = request_id
    return response


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    request_id = getattr(request.state, "request_id", "unknown")
    logger.exception("Unhandled application error", extra={"request_id": request_id})
    body = APIErrorResponse(
        error_code="INTERNAL_ERROR",
        detail_de="Interner Serverfehler. Bitte versuche es erneut.",
        detail_en="Internal server error. Please try again.",
        request_id=request_id,
    )
    return JSONResponse(status_code=500, content=body.model_dump())

app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """Detailed health probe covering all subsystems."""
    import redis.asyncio as aioredis
    from sqlalchemy import text as sa_text

    from app.database import engine

    checks: dict[str, str] = {}

    # Database
    try:
        async with engine.connect() as conn:
            await conn.execute(sa_text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as exc:
        checks["database"] = f"error: {type(exc).__name__}"

    # Redis
    try:
        r = aioredis.from_url(settings.redis_url, socket_connect_timeout=2, socket_timeout=2)
        await r.ping()
        await r.aclose()
        checks["redis"] = "ok"
    except Exception as exc:
        checks["redis"] = f"error: {type(exc).__name__}"

    # MinIO
    try:
        import urllib.request

        url = f"http://{settings.minio_endpoint}/minio/health/live"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=2) as resp:
            checks["minio"] = "ok" if resp.status == 200 else f"status:{resp.status}"
    except Exception as exc:
        checks["minio"] = f"error: {type(exc).__name__}"

    all_ok = all(v == "ok" for v in checks.values())
    uptime_seconds = round(time.monotonic() - _START_TIME, 1)

    return {
        "status": "ok" if all_ok else "degraded",
        "version": settings.app_version,
        "uptime_seconds": uptime_seconds,
        "checks": checks,
    }
