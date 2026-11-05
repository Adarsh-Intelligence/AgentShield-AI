from __future__ import annotations

from fastapi import APIRouter
from backend.app.schemas.evaluation import (
    EvaluationRequest,
    EvaluationResultSchema,
)
from backend.app.services.evaluation_service import EvaluationService

router = APIRouter()


@router.post("/evaluate", response_model=EvaluationResultSchema)
@router.post("/evaluations/evaluate", response_model=EvaluationResultSchema)
def evaluate_response(eval_req: EvaluationRequest):
    """
    Perform ad-hoc evaluation of an AI response using exact match,
    normalized text, keyword validation, semantic similarity, or structured JSON.
    """
    return EvaluationService.evaluate_response_standalone(eval_req)

