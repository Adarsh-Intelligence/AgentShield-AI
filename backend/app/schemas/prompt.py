from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class PromptVersionCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    version: str = Field(..., min_length=1, max_length=50)
    system_prompt: str = Field(..., min_length=1)
    user_template: Optional[str] = None
    description: Optional[str] = None
    prompt_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class PromptVersionResponse(BaseModel):
    id: str
    project_id: str
    name: str
    version: str
    system_prompt: str
    user_template: Optional[str] = None
    description: Optional[str] = None
    is_immutable: bool
    prompt_metadata: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True


class PromptRegressionCompareRequest(BaseModel):
    baseline_prompt_version_id: str
    candidate_prompt_version_id: str
    test_suite_id: str
    agent_id: str
    pass_rate_tolerance: float = Field(default=0.0, ge=0.0, le=1.0)  # allowable drop


class RegressionDetail(BaseModel):
    test_case_id: str
    test_case_name: str
    baseline_passed: bool
    candidate_passed: bool
    baseline_score: float
    candidate_score: float
    status: str  # REGRESSION, IMPROVEMENT, UNCHANGED


class PromptComparisonResponse(BaseModel):
    baseline_version: str
    candidate_version: str
    baseline_pass_rate: float
    candidate_pass_rate: float
    pass_rate_difference: float
    is_regression: bool
    regression_summary: str
    new_failures_count: int
    resolved_failures_count: int
    latency_difference_ms: float
    token_usage_difference: int
    cost_difference: float
    details: List[RegressionDetail]

