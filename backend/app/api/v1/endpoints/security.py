from __future__ import annotations

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from backend.app.api.deps import verify_project_access
from backend.app.database.session import get_db
from backend.app.models.project import Project
from backend.app.schemas.security import (
    SecurityFindingResponse,
    SecurityScanRequest,
    SecurityScanSummary,
)
from backend.app.services.security_service import SecurityService

router = APIRouter()


@router.post(
    "/projects/{project_id}/security/scan",
    response_model=SecurityScanSummary,
    status_code=status.HTTP_200_OK,
)
async def run_security_scan(
    scan_req: SecurityScanRequest,
    project: Project = Depends(verify_project_access),
    db: Session = Depends(get_db),
):
    """
    Run automated AI security tests on an agent:
    Prompt Injection, Sensitive Data Leakage, Jailbreak Testing,
    Unsafe Tool Invocation, and Output Safety.
    """
    return await SecurityService.execute_security_scan(db, project, scan_req)


@router.get(
    "/projects/{project_id}/security/findings",
    response_model=List[SecurityFindingResponse],
)
def get_security_findings(
    category: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    limit: int = 50,
    skip: int = 0,
    project: Project = Depends(verify_project_access),
    db: Session = Depends(get_db),
):
    """List security findings identified for a project."""
    findings = SecurityService.get_security_findings(
        db, project, category=category, severity=severity, limit=limit, skip=skip
    )
    return [SecurityFindingResponse.model_validate(f) for f in findings]


@router.get(
    "/projects/{project_id}/security/findings/{finding_id}",
    response_model=SecurityFindingResponse,
)
def get_security_finding(
    finding_id: str,
    project: Project = Depends(verify_project_access),
    db: Session = Depends(get_db),
):
    """Retrieve full details of a specific security finding."""
    finding = SecurityService.get_security_finding_by_id(db, finding_id, project)
    return SecurityFindingResponse.model_validate(finding)

