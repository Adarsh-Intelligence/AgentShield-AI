from __future__ import annotations

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from backend.app.api.deps import verify_project_access
from backend.app.database.session import get_db
from backend.app.models.project import Project
from backend.app.schemas.prompt import (
    PromptComparisonResponse,
    PromptRegressionCompareRequest,
    PromptVersionCreate,
    PromptVersionResponse,
)
from backend.app.services.regression_service import RegressionService

router = APIRouter()


@router.post("/projects/{project_id}/prompts", response_model=PromptVersionResponse, status_code=status.HTTP_201_CREATED)
def create_prompt_version(
    prompt_in: PromptVersionCreate,
    project: Project = Depends(verify_project_access),
    db: Session = Depends(get_db),
):
    """Create an immutable prompt version for regression tracking."""
    return RegressionService.create_prompt_version(db, project, prompt_in)


@router.get("/projects/{project_id}/prompts", response_model=List[PromptVersionResponse])
def get_prompt_versions(
    project: Project = Depends(verify_project_access),
    db: Session = Depends(get_db),
):
    """List all prompt versions in a project."""
    return RegressionService.get_prompt_versions(db, project)


@router.get("/projects/{project_id}/prompts/{prompt_id}", response_model=PromptVersionResponse)
def get_prompt_version(
    prompt_id: str,
    project: Project = Depends(verify_project_access),
    db: Session = Depends(get_db),
):
    """Get single prompt version by ID."""
    return RegressionService.get_prompt_version_by_id(db, prompt_id, project.id)


@router.post("/projects/{project_id}/prompts/compare", response_model=PromptComparisonResponse)
async def compare_prompt_versions(
    compare_req: PromptRegressionCompareRequest,
    project: Project = Depends(verify_project_access),
    db: Session = Depends(get_db),
):
    """
    Run the same test dataset against two prompt versions,
    comparing pass rates, scores, latency, tokens, cost, and identifying regressions.
    """
    return await RegressionService.compare_prompt_versions(db, project, compare_req)

