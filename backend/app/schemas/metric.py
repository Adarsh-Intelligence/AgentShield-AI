from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel


class PerformanceMetricResponse(BaseModel):
    id: str
    test_run_id: str
    agent_id: str
    avg_latency_ms: float
    p50_latency_ms: float
    p95_latency_ms: float
    total_tokens: int
    prompt_tokens: int
    completion_tokens: int
    estimated_cost: float
    error_rate: float
    pass_rate: float
    metrics_breakdown: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True


class ProjectAggregatedMetrics(BaseModel):
    project_id: str
    total_runs: int
    total_evaluations: int
    avg_latency_ms: float
    overall_pass_rate: float
    total_tokens_consumed: int
    total_estimated_cost: float
    total_security_findings: int

