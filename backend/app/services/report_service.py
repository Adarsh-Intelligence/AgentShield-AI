from __future__ import annotations

import csv
import io
from typing import List, Optional
from sqlalchemy.orm import Session
from backend.app.core.exceptions import EntityNotFoundException
from backend.app.models.project import Project
from backend.app.models.report import EvaluationReport
from backend.app.models.test_run import TestRun


class ReportService:
    @staticmethod
    def get_report_by_id(db: Session, report_id: str, project: Project) -> EvaluationReport:
        report = (
            db.query(EvaluationReport)
            .filter(EvaluationReport.id == report_id, EvaluationReport.project_id == project.id)
            .first()
        )
        if not report:
            raise EntityNotFoundException("EvaluationReport", report_id)
        return report

    @staticmethod
    def get_reports_by_project(
        db: Session, project: Project, report_type: Optional[str] = None
    ) -> List[EvaluationReport]:
        query = db.query(EvaluationReport).filter(EvaluationReport.project_id == project.id)
        if report_type:
            query = query.filter(EvaluationReport.report_type == report_type)
        return query.order_by(EvaluationReport.created_at.desc()).all()

    @staticmethod
    def export_test_run_csv(db: Session, test_run_id: str, project: Project) -> str:
        test_run = (
            db.query(TestRun)
            .join(TestRun.test_suite)
            .filter(TestRun.id == test_run_id, TestRun.test_suite.has(project_id=project.id))
            .first()
        )
        if not test_run:
            raise EntityNotFoundException("TestRun", test_run_id)

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "Result ID",
            "Test Case ID",
            "Evaluation Method",
            "Score",
            "Passed",
            "Duration (ms)",
            "Prompt Tokens",
            "Completion Tokens",
            "Estimated Cost (USD)",
            "Failure Explanation",
        ])

        for r in test_run.results:
            writer.writerow([
                r.id,
                r.test_case_id,
                r.evaluation_method,
                r.score,
                r.passed,
                r.execution_duration_ms,
                r.prompt_tokens,
                r.completion_tokens,
                r.estimated_cost,
                r.failure_explanation or "",
            ])

        return output.getvalue()

