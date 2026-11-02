from __future__ import annotations

from fastapi import APIRouter
from backend.app.api.v1.endpoints import (
    agents,
    auth,
    evaluations,
    metrics,
    projects,
    prompts,
    reports,
    security,
    test_runs,
    test_suites,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])
api_router.include_router(agents.router, tags=["Agents"])
api_router.include_router(test_suites.router, tags=["Test Suites & Cases"])
api_router.include_router(test_runs.router, tags=["Test Runs"])
api_router.include_router(evaluations.router, tags=["Evaluations"])
api_router.include_router(prompts.router, tags=["Prompts & Regressions"])
api_router.include_router(security.router, tags=["Security"])
api_router.include_router(metrics.router, tags=["Metrics"])
api_router.include_router(reports.router, tags=["Reports"])

