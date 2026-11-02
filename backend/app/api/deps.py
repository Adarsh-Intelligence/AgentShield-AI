from __future__ import annotations

from typing import Generator
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from backend.app.core.exceptions import (
    EntityNotFoundException,
    ForbiddenException,
    UnauthorizedException,
)
from backend.app.core.security import decode_jwt_token
from backend.app.database.session import get_db
from backend.app.models.project import Project
from backend.app.models.user import User

security_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db),
) -> User:
    if not credentials:
        raise UnauthorizedException("Authentication credentials were not provided.")

    token = credentials.credentials
    payload = decode_jwt_token(token, expected_type="access")
    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedException("Invalid token payload: missing subject.")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise UnauthorizedException("User no longer exists.")
    if not user.is_active:
        raise UnauthorizedException("User account is inactive.")

    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise ForbiddenException("Administrator privileges required.")
    return current_user


def verify_project_access(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Project:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise EntityNotFoundException("Project", project_id)

    # Admin has access to all projects; Developers can only access their owned projects
    if current_user.role != "admin" and project.owner_id != current_user.id:
        raise ForbiddenException("You do not have access to this project.")

    return project

