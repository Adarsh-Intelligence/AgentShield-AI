from __future__ import annotations

from typing import Any, Dict, List, Optional, TYPE_CHECKING
from sqlalchemy import Boolean, ForeignKey, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from backend.app.models.project import Project
    from backend.app.models.test_run import TestRun


class PromptVersion(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "prompt_versions"
    __table_args__ = (
        UniqueConstraint("project_id", "name", "version", name="uq_project_prompt_version"),
    )

    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    system_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    user_template: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_immutable: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    prompt_metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    project: Mapped["Project"] = relationship("Project", back_populates="prompts")
    test_runs: Mapped[List["TestRun"]] = relationship("TestRun", back_populates="prompt_version")

