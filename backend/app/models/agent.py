from __future__ import annotations

from typing import Any, Dict, List, Optional, TYPE_CHECKING
from sqlalchemy import Boolean, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from backend.app.models.project import Project
    from backend.app.models.test_run import TestRun
    from backend.app.models.security import SecurityFinding


class Agent(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "agents"

    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    provider_type: Mapped[str] = mapped_column(String(50), nullable=False)  # groq, ollama, openai_compatible, mock
    api_endpoint: Mapped[str] = mapped_column(String(1024), nullable=False)
    model_name: Mapped[str] = mapped_column(String(255), nullable=False)
    timeout_seconds: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    custom_headers: Mapped[Dict[str, str]] = mapped_column(JSON, default=dict, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    project: Mapped["Project"] = relationship("Project", back_populates="agents")
    credential: Mapped[Optional["AgentCredential"]] = relationship("AgentCredential", back_populates="agent", uselist=False, cascade="all, delete-orphan")
    test_runs: Mapped[List["TestRun"]] = relationship("TestRun", back_populates="agent", cascade="all, delete-orphan")
    security_findings: Mapped[List["SecurityFinding"]] = relationship("SecurityFinding", back_populates="agent", cascade="all, delete-orphan")


class AgentCredential(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "agent_credentials"

    agent_id: Mapped[str] = mapped_column(String(36), ForeignKey("agents.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    encrypted_api_key: Mapped[str] = mapped_column(Text, nullable=False)

    agent: Mapped["Agent"] = relationship("Agent", back_populates="credential")

