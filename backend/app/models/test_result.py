from __future__ import annotations

from typing import Any, Dict, Optional, TYPE_CHECKING
from sqlalchemy import Boolean, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from backend.app.models.test_run import TestRun
    from backend.app.models.test_case import TestCase


class TestResult(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "test_results"

    test_run_id: Mapped[str] = mapped_column(String(36), ForeignKey("test_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    test_case_id: Mapped[str] = mapped_column(String(36), ForeignKey("test_cases.id", ondelete="CASCADE"), nullable=False, index=True)

    actual_response: Mapped[str] = mapped_column(Text, nullable=False)
    expected_response: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    evaluation_method: Mapped[str] = mapped_column(String(50), nullable=False)
    score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    passed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    failure_explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    execution_duration_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    prompt_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completion_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    estimated_cost: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    tool_call_details: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    test_run: Mapped["TestRun"] = relationship("TestRun", back_populates="results")
    test_case: Mapped["TestCase"] = relationship("TestCase", back_populates="test_results")

