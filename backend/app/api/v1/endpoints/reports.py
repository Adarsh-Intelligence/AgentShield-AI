from __future__ import annotations

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session
from backend.app.api.deps import verify_project_access
from backend.app.database.session import get_db
from backend.app.models.project import Project
from backend.app.schemas.report import ReportResponse
from backend.app.services.report_service import ReportService

router = APIRouter()


@router.get("/projects/{project_id}/reports", response_model=List[ReportResponse])
def get_reports(
    report_type: Optional[str] = Query(None, pattern="^(test_run|regression|security)$"),
    project: Project = Depends(verify_project_access),
    db: Session = Depends(get_db),
):
    """List all generated evaluation, regression, and security reports for a project."""
    return ReportService.get_reports_by_project(db, project, report_type)


@router.get("/projects/{project_id}/reports/{report_id}", response_model=ReportResponse)
def get_report(
    report_id: str,
    project: Project = Depends(verify_project_access),
    db: Session = Depends(get_db),
):
    """Retrieve full structured JSON evaluation report."""
    return ReportService.get_report_by_id(db, report_id, project)


@router.get("/projects/{project_id}/test-runs/{run_id}/export-csv")
def export_test_run_csv(
    run_id: str,
    project: Project = Depends(verify_project_access),
    db: Session = Depends(get_db),
):
    """Export test run evaluation results as a downloadable CSV."""
    csv_content = ReportService.export_test_run_csv(db, run_id, project)
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=test_run_{run_id}.csv"},
    )

