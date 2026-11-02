from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class AgentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    provider_type: str = Field(..., pattern="^(groq|ollama|openai_compatible|mock)$")
    api_endpoint: str = Field(..., min_length=1, max_length=1024)
    model_name: str = Field(..., min_length=1, max_length=255)
    api_key: Optional[str] = None
    timeout_seconds: int = Field(default=30, ge=1, le=300)
    custom_headers: Optional[Dict[str, str]] = Field(default_factory=dict)


class AgentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    provider_type: Optional[str] = Field(None, pattern="^(groq|ollama|openai_compatible|mock)$")
    api_endpoint: Optional[str] = Field(None, min_length=1, max_length=1024)
    model_name: Optional[str] = Field(None, min_length=1, max_length=255)
    api_key: Optional[str] = None
    timeout_seconds: Optional[int] = Field(None, ge=1, le=300)
    custom_headers: Optional[Dict[str, str]] = None
    is_active: Optional[bool] = None


class AgentResponse(BaseModel):
    id: str
    project_id: str
    name: str
    description: Optional[str] = None
    provider_type: str
    api_endpoint: str
    model_name: str
    timeout_seconds: int
    custom_headers: Dict[str, str]
    is_active: bool
    has_api_key: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AgentTestConnectionResponse(BaseModel):
    success: bool
    provider_type: str
    latency_ms: float
    message: str
    raw_response: Optional[Dict[str, Any]] = None
