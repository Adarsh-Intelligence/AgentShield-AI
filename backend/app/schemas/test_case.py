from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class TestCaseCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    input_prompt: str = Field(..., min_length=1)
    expected_output: Optional[str] = None
    evaluation_method: str = Field(
        default="exact_match",
        pattern="^(exact_match|normalized_text|keyword_validation|semantic_similarity|structured_json|llm_judge)$",
    )
    required_keywords: Optional[List[str]] = Field(default_factory=list)
    forbidden_keywords: Optional[List[str]] = Field(default_factory=list)
    similarity_threshold: Optional[float] = Field(default=0.8, ge=0.0, le=1.0)
    expected_tool_calls: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    custom_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class TestCaseUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    input_prompt: Optional[str] = Field(None, min_length=1)
    expected_output: Optional[str] = None
    evaluation_method: Optional[str] = Field(
        None,
        pattern="^(exact_match|normalized_text|keyword_validation|semantic_similarity|structured_json|llm_judge)$",
    )
    required_keywords: Optional[List[str]] = None
    forbidden_keywords: Optional[List[str]] = None
    similarity_threshold: Optional[float] = Field(None, ge=0.0, le=1.0)
    expected_tool_calls: Optional[List[Dict[str, Any]]] = None
    custom_metadata: Optional[Dict[str, Any]] = None


class TestCaseResponse(BaseModel):
    id: str
    test_suite_id: str
    name: str
    input_prompt: str
    expected_output: Optional[str] = None
    evaluation_method: str
    required_keywords: List[str]
    forbidden_keywords: List[str]
    similarity_threshold: float
    expected_tool_calls: List[Dict[str, Any]]
    custom_metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

