from __future__ import annotations

from typing import Any, Dict, List, TYPE_CHECKING
from sqlalchemy import ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from backend.app.models.user import User
    from backend.app.models.agent import Agent
    from backend.app.models.test_suite import TestSuite
    from backend.app.models.prompt import PromptVersion
    from backend.app.models.security import SecurityFinding
    from backend.app.models.report import EvaluationReport


class Project(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "projects"

    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    owner_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    config: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    owner: Mapped["User"] = relationship("User", back_populates="projects")
    agents: Mapped[List["Agent"]] = relationship("Agent", back_populates="project", cascade="all, delete-orphan")
    test_suites: Mapped[List["TestSuite"]] = relationship("TestSuite", back_populates="project", cascade="all, delete-orphan")
    prompts: Mapped[List["PromptVersion"]] = relationship("PromptVersion", back_populates="project", cascade="all, delete-orphan")
    security_findings: Mapped[List["SecurityFinding"]] = relationship("SecurityFinding", back_populates="project", cascade="all, delete-orphan")
    reports: Mapped[List["EvaluationReport"]] = relationship("EvaluationReport", back_populates="project", cascade="all, delete-orphan")

