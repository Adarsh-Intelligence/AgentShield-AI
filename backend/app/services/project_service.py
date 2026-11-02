from __future__ import annotations

from typing import List, Optional
from sqlalchemy.orm import Session
from backend.app.core.exceptions import EntityNotFoundException, ForbiddenException
from backend.app.models.project import Project
from backend.app.models.user import User
from backend.app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectService:
    @staticmethod
    def create_project(db: Session, project_in: ProjectCreate, owner: User) -> Project:
        project = Project(
            name=project_in.name,
            description=project_in.description,
            owner_id=owner.id,
            config=project_in.config or {},
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def get_projects(db: Session, user: User, skip: int = 0, limit: int = 50) -> List[Project]:
        query = db.query(Project)
        if user.role != "admin":
            query = query.filter(Project.owner_id == user.id)
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def get_project_by_id(db: Session, project_id: str, user: User) -> Project:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise EntityNotFoundException("Project", project_id)
        if user.role != "admin" and project.owner_id != user.id:
            raise ForbiddenException("You do not own this project.")
        return project

    @staticmethod
    def update_project(db: Session, project_id: str, project_in: ProjectUpdate, user: User) -> Project:
        project = ProjectService.get_project_by_id(db, project_id, user)
        if project_in.name is not None:
            project.name = project_in.name
        if project_in.description is not None:
            project.description = project_in.description
        if project_in.config is not None:
            project.config = project_in.config

        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def delete_project(db: Session, project_id: str, user: User) -> None:
        project = ProjectService.get_project_by_id(db, project_id, user)
        db.delete(project)
        db.commit()

