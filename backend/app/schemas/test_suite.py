from __future__ import annotations

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class TestSuiteCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class TestSuiteUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None


class TestSuiteResponse(BaseModel):
    id: str
    project_id: str
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

