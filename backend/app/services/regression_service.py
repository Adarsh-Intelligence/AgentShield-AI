from __future__ import annotations

from typing import List, Optional
from sqlalchemy.orm import Session
from backend.app.core.exceptions import (
    BadRequestException,
    ConflictException,
    EntityNotFoundException,
)
from backend.app.engines.regression_engine import RegressionEngine
from backend.app.models.agent import Agent
from backend.app.models.project import Project
from backend.app.models.prompt import PromptVersion
from backend.app.models.report import EvaluationReport
from backend.app.models.test_run import TestRun
from backend.app.models.test_suite import TestSuite
from backend.app.schemas.prompt import (
    PromptComparisonResponse,
    PromptRegressionCompareRequest,
    PromptVersionCreate,
)
from backend.app.services.evaluation_service import EvaluationService


class RegressionService:
    @staticmethod
    def create_prompt_version(
        db: Session, project: Project, prompt_in: PromptVersionCreate
    ) -> PromptVersion:
        # Check uniqueness of (project_id, name, version)
        existing = (
            db.query(PromptVersion)
            .filter(
                PromptVersion.project_id == project.id,
                PromptVersion.name == prompt_in.name,
                PromptVersion.version == prompt_in.version,
            )
            .first()
        )
        if existing:
            raise ConflictException(
                f"Prompt '{prompt_in.name}' with version '{prompt_in.version}' already exists."
            )

        prompt_version = PromptVersion(
            project_id=project.id,
            name=prompt_in.name,
            version=prompt_in.version,
            system_prompt=prompt_in.system_prompt,
            user_template=prompt_in.user_template,
            description=prompt_in.description,
            is_immutable=True,
            prompt_metadata=prompt_in.prompt_metadata or {},
        )
        db.add(prompt_version)
        db.commit()
        db.refresh(prompt_version)
        return prompt_version

    @staticmethod
    def get_prompt_versions(db: Session, project: Project) -> List[PromptVersion]:
        return (
            db.query(PromptVersion)
            .filter(PromptVersion.project_id == project.id)
            .order_by(PromptVersion.created_at.desc())
            .all()
        )

    @staticmethod
    def get_prompt_version_by_id(
        db: Session, prompt_id: str, project_id: Optional[str] = None
    ) -> PromptVersion:
        query = db.query(PromptVersion).filter(PromptVersion.id == prompt_id)
        if project_id:
            query = query.filter(PromptVersion.project_id == project_id)
        prompt = query.first()
        if not prompt:
            raise EntityNotFoundException("PromptVersion", prompt_id)
        return prompt

    @classmethod
    async def compare_prompt_versions(
        cls,
        db: Session,
        project: Project,
        compare_req: PromptRegressionCompareRequest,
    ) -> PromptComparisonResponse:
        baseline_prompt = cls.get_prompt_version_by_id(
            db, compare_req.baseline_prompt_version_id, project.id
        )
        candidate_prompt = cls.get_prompt_version_by_id(
            db, compare_req.candidate_prompt_version_id, project.id
        )

        test_suite = (
            db.query(TestSuite)
            .filter(TestSuite.id == compare_req.test_suite_id, TestSuite.project_id == project.id)
            .first()
        )
        if not test_suite:
            raise EntityNotFoundException("TestSuite", compare_req.test_suite_id)

        agent = (
            db.query(Agent)
            .filter(Agent.id == compare_req.agent_id, Agent.project_id == project.id)
            .first()
        )
        if not agent:
            raise EntityNotFoundException("Agent", compare_req.agent_id)

        # Run test suite on baseline prompt
        baseline_run = await EvaluationService.execute_test_run(
            db=db,
            test_suite_id=test_suite.id,
            agent_id=agent.id,
            prompt_version_id=baseline_prompt.id,
        )

        # Run test suite on candidate prompt
        candidate_run = await EvaluationService.execute_test_run(
            db=db,
            test_suite_id=test_suite.id,
            agent_id=agent.id,
            prompt_version_id=candidate_prompt.id,
        )

        comparison = RegressionEngine.compare_runs(
            baseline_run=baseline_run,
            candidate_run=candidate_run,
            baseline_prompt=baseline_prompt,
            candidate_prompt=candidate_prompt,
            pass_rate_tolerance=compare_req.pass_rate_tolerance,
        )

        # Persist regression report
        report = EvaluationReport(
            project_id=project.id,
            test_run_id=candidate_run.id,
            report_type="regression",
            title=f"Regression Report: {baseline_prompt.version} vs {candidate_prompt.version}",
            summary={
                "baseline_version": baseline_prompt.version,
                "candidate_version": candidate_prompt.version,
                "is_regression": comparison.is_regression,
                "pass_rate_diff": comparison.pass_rate_difference,
                "new_failures": comparison.new_failures_count,
                "resolved_failures": comparison.resolved_failures_count,
            },
            content=comparison.model_dump(),
        )
        db.add(report)
        db.commit()

        return comparison

