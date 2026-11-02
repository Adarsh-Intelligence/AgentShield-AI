from __future__ import annotations

from typing import Any, Dict, Optional, TYPE_CHECKING
from sqlalchemy import ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from backend.app.models.project import Project
    from backend.app.models.agent import Agent
    from backend.app.models.test_run import TestRun


class SecurityFinding(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "security_findings"

    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_id: Mapped[str] = mapped_column(String(36), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)
    test_run_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("test_runs.id", ondelete="SET NULL"), nullable=True, index=True)

    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # critical, high, medium, low, informational
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    test_input: Mapped[str] = mapped_column(Text, nullable=False)
    observed_output: Mapped[str] = mapped_column(Text, nullable=False)
    evidence: Mapped[str] = mapped_column(Text, nullable=False)
    reproduction_steps: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    finding_metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    project: Mapped["Project"] = relationship("Project", back_populates="security_findings")
    agent: Mapped["Agent"] = relationship("Agent", back_populates="security_findings")
    test_run: Mapped[Optional["TestRun"]] = relationship("TestRun", back_populates="security_findings")

