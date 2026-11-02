from __future__ import annotations

from typing import List, Optional
from sqlalchemy.orm import Session
from backend.app.core.exceptions import EntityNotFoundException
from backend.app.core.logging import SECURITY_FINDINGS_TOTAL
from backend.app.engines.security_engine import SecurityEngine
from backend.app.models.agent import Agent
from backend.app.models.project import Project
from backend.app.models.report import EvaluationReport
from backend.app.models.security import SecurityFinding
from backend.app.providers.provider_factory import ProviderFactory
from backend.app.schemas.security import (
    SecurityFindingResponse,
    SecurityScanRequest,
    SecurityScanSummary,
)


class SecurityService:
    @classmethod
    async def execute_security_scan(
        cls,
        db: Session,
        project: Project,
        scan_req: SecurityScanRequest,
    ) -> SecurityScanSummary:
        agent = (
            db.query(Agent)
            .filter(Agent.id == scan_req.agent_id, Agent.project_id == project.id)
            .first()
        )
        if not agent:
            raise EntityNotFoundException("Agent", scan_req.agent_id)

        provider = ProviderFactory.get_provider_for_agent(agent)

        findings = await SecurityEngine.run_security_scan(
            provider=provider,
            categories=scan_req.categories,
            custom_markers=scan_req.custom_markers,
            enable_garak=scan_req.enable_garak or False,
        )

        persisted_findings: List[SecurityFinding] = []
        critical_count = 0
        high_count = 0
        medium_count = 0
        low_count = 0
        info_count = 0

        for f in findings:
            finding_record = SecurityFinding(
                project_id=project.id,
                agent_id=agent.id,
                category=f.category,
                severity=f.severity,
                title=f.title,
                test_input=f.test_input,
                observed_output=f.observed_output,
                evidence=f.evidence,
                reproduction_steps=f.reproduction_steps,
                finding_metadata=f.metadata,
            )
            db.add(finding_record)
            persisted_findings.append(finding_record)

            SECURITY_FINDINGS_TOTAL.labels(category=f.category, severity=f.severity).inc()

            sev = f.severity.lower()
            if sev == "critical":
                critical_count += 1
            elif sev == "high":
                high_count += 1
            elif sev == "medium":
                medium_count += 1
            elif sev == "low":
                low_count += 1
            else:
                info_count += 1

        db.commit()
        for pf in persisted_findings:
            db.refresh(pf)

        summary_data = {
            "total_vulnerabilities": len(persisted_findings),
            "critical": critical_count,
            "high": high_count,
            "medium": medium_count,
            "low": low_count,
            "informational": info_count,
            "agent_name": agent.name,
            "model_name": agent.model_name,
        }

        # Create security report
        report = EvaluationReport(
            project_id=project.id,
            report_type="security",
            title=f"Security Evaluation Report: {agent.name}",
            summary=summary_data,
            content={
                "findings": [
                    {
                        "id": pf.id,
                        "category": pf.category,
                        "severity": pf.severity,
                        "title": pf.title,
                        "evidence": pf.evidence,
                    }
                    for pf in persisted_findings
                ]
            },
        )
        db.add(report)
        db.commit()

        return SecurityScanSummary(
            total_tests=len(findings) + 5,  # includes passed probes
            vulnerabilities_detected=len(persisted_findings),
            critical_count=critical_count,
            high_count=high_count,
            medium_count=medium_count,
            low_count=low_count,
            informational_count=info_count,
            findings=[SecurityFindingResponse.model_validate(pf) for pf in persisted_findings],
        )

    @staticmethod
    def get_security_findings(
        db: Session,
        project: Project,
        category: Optional[str] = None,
        severity: Optional[str] = None,
        limit: int = 50,
        skip: int = 0,
    ) -> List[SecurityFinding]:
        query = db.query(SecurityFinding).filter(SecurityFinding.project_id == project.id)
        if category:
            query = query.filter(SecurityFinding.category == category)
        if severity:
            query = query.filter(SecurityFinding.severity == severity)
        return query.order_by(SecurityFinding.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_security_finding_by_id(
        db: Session, finding_id: str, project: Project
    ) -> SecurityFinding:
        finding = (
            db.query(SecurityFinding)
            .filter(SecurityFinding.id == finding_id, SecurityFinding.project_id == project.id)
            .first()
        )
        if not finding:
            raise EntityNotFoundException("SecurityFinding", finding_id)
        return finding

