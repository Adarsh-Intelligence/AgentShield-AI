from __future__ import annotations

from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from backend.app.models.test_suite import TestSuite
    from backend.app.models.agent import Agent
    from backend.app.models.prompt import PromptVersion
    from backend.app.models.test_result import TestResult
    from backend.app.models.metric import PerformanceMetric
    from backend.app.models.report import EvaluationReport
    from backend.app.models.security import SecurityFinding


class TestRun(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "test_runs"

    test_suite_id: Mapped[str] = mapped_column(String(36), ForeignKey("test_suites.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_id: Mapped[str] = mapped_column(String(36), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)
    prompt_version_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("prompt_versions.id", ondelete="SET NULL"), nullable=True, index=True)

    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False, index=True)  # pending, running, completed, failed, cancelled
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    total_cases: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    passed_cases: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    failed_cases: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    pass_rate: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    execution_duration_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    test_suite: Mapped["TestSuite"] = relationship("TestSuite", back_populates="test_runs")
    agent: Mapped["Agent"] = relationship("Agent", back_populates="test_runs")
    prompt_version: Mapped[Optional["PromptVersion"]] = relationship("PromptVersion", back_populates="test_runs")
    results: Mapped[List["TestResult"]] = relationship("TestResult", back_populates="test_run", cascade="all, delete-orphan")
    metrics: Mapped[Optional["PerformanceMetric"]] = relationship("PerformanceMetric", back_populates="test_run", uselist=False, cascade="all, delete-orphan")
    reports: Mapped[List["EvaluationReport"]] = relationship("EvaluationReport", back_populates="test_run", cascade="all, delete-orphan")
    security_findings: Mapped[List["SecurityFinding"]] = relationship("SecurityFinding", back_populates="test_run", cascade="all, delete-orphan")

