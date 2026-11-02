from __future__ import annotations

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from backend.app.api.deps import get_current_user
from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.schemas.project import (
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
)
from backend.app.services.project_service import ProjectService

router = APIRouter()


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project_in: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new AI testing project."""
    return ProjectService.create_project(db, project_in, current_user)


@router.get("", response_model=List[ProjectResponse])
def get_projects(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all projects owned by the user (or all projects if admin)."""
    return ProjectService.get_projects(db, current_user, skip=skip, limit=limit)


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get project details by ID with ownership verification."""
    return ProjectService.get_project_by_id(db, project_id, current_user)


@router.patch("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: str,
    project_in: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update project details."""
    return ProjectService.update_project(db, project_id, project_in, current_user)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a project and its associated resources."""
    ProjectService.delete_project(db, project_id, current_user)

