import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.health import router as health_router
from app.api.routes.projects import router as projects_router
from app.core.config import settings
from app.core.logging import logger


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Run startup diagnostics, then yield for the application lifetime."""
    # settings import already validates all required env vars at module load;
    # this block logs confirmation and can run lightweight connectivity checks.
    logger.info(
        "MotionForge API starting",
        extra={
            "cors_origins": settings.backend_cors_origins,
            "app_url": settings.app_url,
            "auth_bypass": settings.auth_bypass,
            "uploadthing_configured": bool(settings.uploadthing_secret),
            "nvidia_model": settings.nvidia_vision_model,
        },
    )
    yield
    logger.info("MotionForge API shutting down")


app = FastAPI(title="MotionForge API", version="1.0.0", lifespan=lifespan)

# ── CORS ──────────────────────────────────────────────────────────────────────
_origins = [o.strip() for o in settings.backend_cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request / response logging middleware ─────────────────────────────────────
@app.middleware("http")
async def _log_requests(request: Request, call_next) -> Response:
    start = time.perf_counter()
    response: Response = await call_next(request)
    duration_ms = round((time.perf_counter() - start) * 1000, 1)

    # Suppress noisy health-check logs at INFO level.
    level = "info" if request.url.path != "/health" else "debug"
    log_fn = logger.info if level == "info" else logger.debug
    log_fn(
        "HTTP request",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status": response.status_code,
            "duration_ms": duration_ms,
        },
    )
    return response


# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(health_router)
app.include_router(projects_router)
