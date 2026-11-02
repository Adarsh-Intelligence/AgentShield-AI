from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SecurityScanRequest(BaseModel):
    agent_id: str
    categories: Optional[List[str]] = Field(
        default=["prompt_injection", "sensitive_data_leakage", "jailbreak", "unsafe_tool_invocation", "output_safety"]
    )
    custom_markers: Optional[List[str]] = Field(default_factory=list)
    timeout_seconds: Optional[int] = Field(default=60, ge=5, le=300)
    enable_garak: Optional[bool] = False


class SecurityFindingResponse(BaseModel):
    id: str
    project_id: str
    agent_id: str
    test_run_id: Optional[str] = None
    category: str
    severity: str
    title: str
    test_input: str
    observed_output: str
    evidence: str
    reproduction_steps: Optional[str] = None
    finding_metadata: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True


class SecurityScanSummary(BaseModel):
    total_tests: int
    vulnerabilities_detected: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    informational_count: int
    findings: List[SecurityFindingResponse]


SecurityScanResponse = SecurityScanSummary
