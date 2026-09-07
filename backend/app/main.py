import os
import time
import shutil
import logging
import asyncio
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from .config import settings, APP_NAME, APP_VERSION, STORAGE_DIR
from .utils.storage import storage
from .api import (
    upload_router,
    analysis_router,
    target_router,
    samples_router,
    export_router,
    drift_router,
    timeseries_router
)

# Structured Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
)
logger = logging.getLogger("edaflow")

# Background TTL cleanup task
async def periodic_storage_cleanup():
    while True:
        try:
            purged = storage.cleanup_old_files()
            if purged > 0:
                logger.info(f"Purged {purged} expired dataset files from storage.")
        except Exception as e:
            logger.error(f"Error during periodic storage cleanup: {e}")
        # Run every 2 hours
        await asyncio.sleep(7200)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(f"Starting {APP_NAME} v{APP_VERSION} in {settings.ENV} mode...")
    # Initial cleanup of stale files
    storage.cleanup_old_files()
    cleanup_task = asyncio.create_task(periodic_storage_cleanup())
    yield
    # Shutdown
    cleanup_task.cancel()
    logger.info(f"Shutting down {APP_NAME}...")

# Initialize Rate Limiter
limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])

app = FastAPI(
    title=f"{APP_NAME} — Automated Dataset Intelligence Platform API",
    version=APP_VERSION,
    description="High-performance backend engine for automated profiling, statistical analysis, multi-method anomaly detection, target intelligence, and insight generation.",
    lifespan=lifespan
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration_ms = round((time.time() - start_time) * 1000, 2)
    logger.info(f"{request.method} {request.url.path} -> {response.status_code} ({duration_ms}ms)")
    return response

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(upload_router, prefix="/api")
app.include_router(analysis_router, prefix="/api")
app.include_router(target_router, prefix="/api")
app.include_router(samples_router, prefix="/api")
app.include_router(export_router, prefix="/api")
app.include_router(drift_router, prefix="/api")
app.include_router(timeseries_router, prefix="/api")

@app.get("/api/health")
async def health_check():
    """Deep health check: validates service readiness, storage writability, and disk capacity."""
    storage_writable = False
    test_file = STORAGE_DIR / ".health_check_probe"
    try:
        test_file.write_text("ok")
        test_file.unlink()
        storage_writable = True
    except Exception as e:
        logger.error(f"Storage health probe failed: {e}")

    # Check disk usage
    disk_total_gb = 0.0
    disk_free_gb = 0.0
    try:
        usage = shutil.disk_usage(STORAGE_DIR)
        disk_total_gb = round(usage.total / (1024 ** 3), 2)
        disk_free_gb = round(usage.free / (1024 ** 3), 2)
    except Exception as e:
        logger.warning(f"Disk usage probe warning: {e}")

    is_healthy = storage_writable and (disk_free_gb > 0.1)

    return {
        "status": "healthy" if is_healthy else "degraded",
        "app": APP_NAME,
        "version": APP_VERSION,
        "environment": settings.ENV,
        "storage": {
            "path": str(STORAGE_DIR),
            "writable": storage_writable,
            "disk_total_gb": disk_total_gb,
            "disk_free_gb": disk_free_gb
        },
        "loaded_samples_count": len(storage.list_samples()),
        "uptime": "operational"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
