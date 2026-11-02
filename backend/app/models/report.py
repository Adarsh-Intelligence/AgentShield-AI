from __future__ import annotations

from typing import Any, Dict, Optional, TYPE_CHECKING
from sqlalchemy import ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from backend.app.models.project import Project
    from backend.app.models.test_run import TestRun


class EvaluationReport(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "evaluation_reports"

    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    test_run_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("test_runs.id", ondelete="SET NULL"), nullable=True, index=True)

    report_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # test_run, regression, security
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    summary: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    content: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    raw_markdown: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    project: Mapped["Project"] = relationship("Project", back_populates="reports")
    test_run: Mapped[Optional["TestRun"]] = relationship("TestRun", back_populates="reports")

