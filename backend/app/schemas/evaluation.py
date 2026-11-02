from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class EvaluationRequest(BaseModel):
    actual_response: str
    expected_response: Optional[str] = None
    evaluation_method: str = Field(
        ...,
        pattern="^(exact_match|normalized_text|keyword_validation|semantic_similarity|structured_json|llm_judge)$",
    )
    required_keywords: Optional[List[str]] = Field(default_factory=list)
    forbidden_keywords: Optional[List[str]] = Field(default_factory=list)
    similarity_threshold: Optional[float] = Field(default=0.8, ge=0.0, le=1.0)
    expected_schema: Optional[Dict[str, Any]] = None
    judge_prompt: Optional[str] = None
    judge_agent_id: Optional[str] = None


class EvaluationResultSchema(BaseModel):
    evaluation_method: str
    score: float
    passed: bool
    failure_explanation: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)

