from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class TestRunCreate(BaseModel):
    test_suite_id: str
    agent_id: str
    prompt_version_id: Optional[str] = None
    async_mode: bool = False


class TestResultResponse(BaseModel):
    id: str
    test_case_id: str
    actual_response: str
    expected_response: Optional[str] = None
    evaluation_method: str
    score: float
    passed: bool
    failure_explanation: Optional[str] = None
    execution_duration_ms: float
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost: float
    tool_call_details: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True


class TestRunResponse(BaseModel):
    id: str
    test_suite_id: str
    agent_id: str
    prompt_version_id: Optional[str] = None
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    total_cases: int
    passed_cases: int
    failed_cases: int
    pass_rate: float
    execution_duration_ms: float
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TestRunDetailResponse(TestRunResponse):
    results: List[TestResultResponse] = []

