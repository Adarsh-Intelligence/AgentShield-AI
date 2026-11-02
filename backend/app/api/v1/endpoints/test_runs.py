from __future__ import annotations

import asyncio
from typing import List
from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy.orm import Session
from backend.app.api.deps import verify_project_access
from backend.app.core.exceptions import EntityNotFoundException
from backend.app.database.session import get_db
from backend.app.models.project import Project
from backend.app.models.test_run import TestRun
from backend.app.schemas.test_run import (
    TestRunCreate,
    TestRunDetailResponse,
    TestRunResponse,
)
from backend.app.services.evaluation_service import EvaluationService
from backend.app.tasks.test_tasks import execute_test_suite_job

router = APIRouter()


@router.post("/projects/{project_id}/test-runs", response_model=TestRunResponse, status_code=status.HTTP_201_CREATED)
async def create_test_run(
    run_in: TestRunCreate,
    background_tasks: BackgroundTasks,
    project: Project = Depends(verify_project_access),
    db: Session = Depends(get_db),
):
    """
    Trigger execution of a test suite against an AI agent.
    If async_mode is True, schedules evaluation in the background.
    """
    if run_in.async_mode:
        # Pre-create test run in pending status
        test_run = TestRun(
            test_suite_id=run_in.test_suite_id,
            agent_id=run_in.agent_id,
            prompt_version_id=run_in.prompt_version_id,
            status="pending",
        )
        db.add(test_run)
        db.commit()
        db.refresh(test_run)

        # Dispatch background job
        background_tasks.add_task(
            execute_test_suite_job,
            run_in.test_suite_id,
            run_in.agent_id,
            run_in.prompt_version_id,
        )
        return test_run
    else:
        # Synchronous execution
        return await EvaluationService.execute_test_run(
            db=db,
            test_suite_id=run_in.test_suite_id,
            agent_id=run_in.agent_id,
            prompt_version_id=run_in.prompt_version_id,
        )


@router.get("/projects/{project_id}/test-runs", response_model=List[TestRunResponse])
def get_test_runs(
    project: Project = Depends(verify_project_access),
    db: Session = Depends(get_db),
):
    """List test runs for a project."""
    return (
        db.query(TestRun)
        .join(TestRun.test_suite)
        .filter(TestRun.test_suite.has(project_id=project.id))
        .order_by(TestRun.created_at.desc())
        .all()
    )


@router.get("/projects/{project_id}/test-runs/{run_id}", response_model=TestRunDetailResponse)
def get_test_run(
    run_id: str,
    project: Project = Depends(verify_project_access),
    db: Session = Depends(get_db),
):
    """Retrieve full details of a test run including individual test results."""
    run = (
        db.query(TestRun)
        .join(TestRun.test_suite)
        .filter(TestRun.id == run_id, TestRun.test_suite.has(project_id=project.id))
        .first()
    )
    if not run:
        raise EntityNotFoundException("TestRun", run_id)
    return run

