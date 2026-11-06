from __future__ import annotations

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from sqlalchemy import text
from backend.app.api.v1.router import api_router
from backend.app.config import settings
from backend.app.core.logging import logger, setup_logging
from backend.app.core.middleware import (
    RequestCorrelationMiddleware,
    RequestSizeLimitMiddleware,
    SecurityHeadersMiddleware,
    register_error_handlers,
)
from backend.app.database.session import SessionLocal, init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    setup_logging()
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION} [{settings.APP_ENV}]")
    if settings.DATABASE_URL.startswith("sqlite"):
        init_db()
    yield
    # Shutdown
    logger.info("Shutting down AgentShield AI application.")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Production-Ready AI Agent Testing, Security & Evaluation Platform Backend",
    openapi_url="/api/v1/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Custom Middlewares (order matters: outer to inner)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestCorrelationMiddleware)
app.add_middleware(RequestSizeLimitMiddleware)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Error handlers
register_error_handlers(app)

# Include API Router
app.include_router(api_router, prefix="/api/v1")


# Static directory
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", response_class=HTMLResponse, tags=["Viewer"])
@app.get("/ui", response_class=HTMLResponse, tags=["Viewer"])
@app.get("/app", response_class=HTMLResponse, tags=["Viewer"])
def root_viewer():
    """Interactive Liquid Glass visual dashboard and platform UI."""
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path, media_type="text/html")
    root_path = os.path.abspath("AgentShield AI – Liquid Glass.html")
    if os.path.exists(root_path):
        return FileResponse(root_path, media_type="text/html")
    return HTMLResponse("<h1>AgentShield AI Platform</h1><p>Static index.html not found.</p>")


@app.get("/health", status_code=status.HTTP_200_OK, tags=["System"])
def health_check():
    """Liveness probe to check if application process is running."""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
    }


@app.get("/ready", status_code=status.HTTP_200_OK, tags=["System"])
def readiness_check():
    """Readiness probe checking database connectivity and core dependencies."""
    db_ok = False
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        db_ok = True
    except Exception as exc:
        logger.error(f"Readiness database probe failed: {exc}")

    if not db_ok:
        return Response(
            content='{"status": "unready", "database": "disconnected"}',
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            media_type="application/json",
        )

    return {
        "status": "ready",
        "database": "connected",
        "app_version": settings.APP_VERSION,
    }


@app.get("/metrics", tags=["System"])
def metrics():
    """Prometheus metrics endpoint."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

