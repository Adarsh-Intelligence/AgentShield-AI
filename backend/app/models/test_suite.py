from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from backend.app.models.project import Project
    from backend.app.models.test_case import TestCase
    from backend.app.models.test_run import TestRun


class TestSuite(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "test_suites"

    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    project: Mapped["Project"] = relationship("Project", back_populates="test_suites")
    test_cases: Mapped[List["TestCase"]] = relationship("TestCase", back_populates="test_suite", cascade="all, delete-orphan")
    test_runs: Mapped[List["TestRun"]] = relationship("TestRun", back_populates="test_suite", cascade="all, delete-orphan")

