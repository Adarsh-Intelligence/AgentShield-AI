from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class ReportCreate(BaseModel):
    project_id: str
    test_run_id: Optional[str] = None
    report_type: str = Field(..., pattern="^(test_run|regression|security)$")
    title: str = Field(..., min_length=1, max_length=255)


class ReportResponse(BaseModel):
    id: str
    project_id: str
    test_run_id: Optional[str] = None
    report_type: str
    title: str
    summary: Dict[str, Any]
    content: Dict[str, Any]
    raw_markdown: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

