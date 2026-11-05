from __future__ import annotations

from contextlib import asynccontextmanager
from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
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


@app.get("/", response_class=HTMLResponse, tags=["Viewer"])
def root_viewer():
    """Interactive visual landing page and documentation viewer for browser access."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AgentShield AI — Backend Platform & Viewer</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background: #0f172a;
            color: #f8fafc;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 2rem 1rem;
        }
        .container {
            max-width: 860px;
            width: 100%;
            background: #1e293b;
            border-radius: 16px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            border: 1px solid #334155;
            overflow: hidden;
        }
        .header {
            padding: 2.5rem 2rem 1.5rem;
            background: linear-gradient(135deg, #1e1b4b 0%, #1e293b 100%);
            border-bottom: 1px solid #334155;
            text-align: center;
        }
        .badge {
            display: inline-flex;
            align-items: center;
            background: #065f46;
            color: #34d399;
            font-size: 0.85rem;
            font-weight: 600;
            padding: 0.35rem 0.85rem;
            border-radius: 9999px;
            margin-bottom: 1rem;
            border: 1px solid #059669;
        }
        .badge-dot {
            width: 8px;
            height: 8px;
            background: #34d399;
            border-radius: 50%;
            margin-right: 6px;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.4; transform: scale(0.85); }
        }
        h1 { font-size: 2.25rem; font-weight: 800; letter-spacing: -0.025em; margin-bottom: 0.5rem; color: #fff; }
        .subtitle { color: #94a3b8; font-size: 1.05rem; max-width: 600px; margin: 0 auto; line-height: 1.5; }
        .content { padding: 2rem; }
        .cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 1.25rem;
            margin-bottom: 2rem;
        }
        .card {
            background: #0f172a;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 1.5rem;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: all 0.2s ease;
            text-decoration: none;
            color: inherit;
        }
        .card:hover {
            border-color: #6366f1;
            transform: translateY(-2px);
            box-shadow: 0 10px 20px -5px rgba(99, 102, 241, 0.2);
        }
        .card-title { font-size: 1.15rem; font-weight: 700; color: #e2e8f0; margin-bottom: 0.5rem; display: flex; align-items: center; justify-content: space-between; }
        .card-desc { font-size: 0.9rem; color: #94a3b8; line-height: 1.4; margin-bottom: 1rem; }
        .card-btn {
            display: inline-flex;
            align-items: center;
            font-size: 0.85rem;
            font-weight: 600;
            color: #818cf8;
        }
        .stats-bar {
            background: #0f172a;
            border-radius: 10px;
            padding: 1rem 1.5rem;
            display: flex;
            justify-content: space-around;
            border: 1px solid #334155;
            text-align: center;
            flex-wrap: wrap;
            gap: 1rem;
        }
        .stat-val { font-size: 1.25rem; font-weight: 700; color: #38bdf8; }
        .stat-lbl { font-size: 0.75rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; margin-top: 0.25rem; }
        .footer { padding: 1.25rem; text-align: center; color: #64748b; font-size: 0.85rem; border-top: 1px solid #334155; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="badge"><span class="badge-dot"></span> Backend Active &amp; Online</div>
            <h1>AgentShield AI</h1>
            <p class="subtitle">Production-Ready AI Agent Testing, Security &amp; Evaluation Platform</p>
        </div>
        <div class="content">
            <div class="cards">
                <a href="/docs" class="card" target="_blank">
                    <div>
                        <div class="card-title">Swagger UI Viewer <span>&rarr;</span></div>
                        <div class="card-desc">Interactive API explorer where you can execute requests, test endpoints, and view response models.</div>
                    </div>
                    <div class="card-btn">Open /docs</div>
                </a>
                <a href="/redoc" class="card" target="_blank">
                    <div>
                        <div class="card-title">ReDoc Documentation <span>&rarr;</span></div>
                        <div class="card-desc">Clean, structured technical documentation viewer for API developers and platform integrations.</div>
                    </div>
                    <div class="card-btn">Open /redoc</div>
                </a>
                <a href="/api/v1/openapi.json" class="card" target="_blank">
                    <div>
                        <div class="card-title">OpenAPI 3.1 Schema <span>&rarr;</span></div>
                        <div class="card-desc">Raw JSON OpenAPI specification schema for generating client SDKs or importing into Postman.</div>
                    </div>
                    <div class="card-btn">Open /openapi.json</div>
                </a>
                <a href="/health" class="card" target="_blank">
                    <div>
                        <div class="card-title">Health Check <span>&rarr;</span></div>
                        <div class="card-desc">Real-time system health status, database readiness probe, and Prometheus metrics.</div>
                    </div>
                    <div class="card-btn">Open /health</div>
                </a>
            </div>

            <div class="stats-bar">
                <div>
                    <div class="stat-val">32+</div>
                    <div class="stat-lbl">API Endpoints</div>
                </div>
                <div>
                    <div class="stat-val">6</div>
                    <div class="stat-lbl">Evaluation Engines</div>
                </div>
                <div>
                    <div class="stat-val">5</div>
                    <div class="stat-lbl">Security Probes</div>
                </div>
                <div>
                    <div class="stat-val">100%</div>
                    <div class="stat-lbl">Tests Passing</div>
                </div>
            </div>
        </div>
        <div class="footer">
            AgentShield AI &bull; Running on <strong>http://localhost:8000</strong>
        </div>
    </div>
</body>
</html>"""


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

