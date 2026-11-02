from __future__ import annotations

from typing import Any, Dict, List, Optional, TYPE_CHECKING
from sqlalchemy import Float, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from backend.app.models.test_suite import TestSuite
    from backend.app.models.test_result import TestResult


class TestCase(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "test_cases"

    test_suite_id: Mapped[str] = mapped_column(String(36), ForeignKey("test_suites.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    input_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    expected_output: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    evaluation_method: Mapped[str] = mapped_column(String(50), default="exact_match", nullable=False)
    
    required_keywords: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    forbidden_keywords: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    similarity_threshold: Mapped[float] = mapped_column(Float, default=0.8, nullable=False)
    expected_tool_calls: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    custom_metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    test_suite: Mapped["TestSuite"] = relationship("TestSuite", back_populates="test_cases")
    test_results: Mapped[List["TestResult"]] = relationship("TestResult", back_populates="test_case", cascade="all, delete-orphan")

