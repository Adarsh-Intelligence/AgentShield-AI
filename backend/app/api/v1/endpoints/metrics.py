from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from backend.app.api.deps import verify_project_access
from backend.app.core.exceptions import EntityNotFoundException
from backend.app.database.session import get_db
from backend.app.models.metric import PerformanceMetric
from backend.app.models.project import Project
from backend.app.models.security import SecurityFinding
from backend.app.models.test_run import TestRun
from backend.app.schemas.metric import (
    PerformanceMetricResponse,
    ProjectAggregatedMetrics,
)

router = APIRouter()


@router.get("/projects/{project_id}/metrics", response_model=ProjectAggregatedMetrics)
def get_project_metrics(
    project: Project = Depends(verify_project_access),
    db: Session = Depends(get_db),
):
    """Get aggregated performance and usage metrics across all test runs in a project."""
    runs = (
        db.query(TestRun)
        .join(TestRun.test_suite)
        .filter(TestRun.test_suite.has(project_id=project.id))
        .all()
    )

    total_runs = len(runs)
    total_evals = sum(r.total_cases for r in runs)
    avg_pass_rate = (sum(r.pass_rate for r in runs) / total_runs) if total_runs > 0 else 0.0
    avg_latency = (sum(r.execution_duration_ms for r in runs) / total_runs) if total_runs > 0 else 0.0

    total_tokens = 0
    total_cost = 0.0
    for r in runs:
        if r.metrics:
            total_tokens += r.metrics.total_tokens
            total_cost += r.metrics.estimated_cost

    sec_count = (
        db.query(func.count(SecurityFinding.id))
        .filter(SecurityFinding.project_id == project.id)
        .scalar()
        or 0
    )

    return ProjectAggregatedMetrics(
        project_id=project.id,
        total_runs=total_runs,
        total_evaluations=total_evals,
        avg_latency_ms=round(avg_latency, 2),
        overall_pass_rate=round(avg_pass_rate, 4),
        total_tokens_consumed=total_tokens,
        total_estimated_cost=round(total_cost, 6),
        total_security_findings=sec_count,
    )


@router.get(
    "/projects/{project_id}/test-runs/{run_id}/metrics",
    response_model=PerformanceMetricResponse,
)
def get_test_run_metrics(
    run_id: str,
    project: Project = Depends(verify_project_access),
    db: Session = Depends(get_db),
):
    """Retrieve detailed latency percentiles, token usage, and costs for a specific test run."""
    run = (
        db.query(TestRun)
        .join(TestRun.test_suite)
        .filter(TestRun.id == run_id, TestRun.test_suite.has(project_id=project.id))
        .first()
    )
    if not run or not run.metrics:
        raise EntityNotFoundException("PerformanceMetric", run_id)
    return run.metrics

