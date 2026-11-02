from __future__ import annotations

from typing import Any, Dict, TYPE_CHECKING
from sqlalchemy import Float, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from backend.app.models.test_run import TestRun
    from backend.app.models.agent import Agent


class PerformanceMetric(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "performance_metrics"

    test_run_id: Mapped[str] = mapped_column(String(36), ForeignKey("test_runs.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    agent_id: Mapped[str] = mapped_column(String(36), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)

    avg_latency_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    p50_latency_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    p95_latency_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    total_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    prompt_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completion_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    estimated_cost: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    error_rate: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    pass_rate: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    metrics_breakdown: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    test_run: Mapped["TestRun"] = relationship("TestRun", back_populates="metrics")

