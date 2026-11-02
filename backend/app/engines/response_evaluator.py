from __future__ import annotations

import json
import os
import re
import string
import unicodedata
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import numpy as np

# Ensure HuggingFace does not hang attempting to reach network in isolated environments
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")


@dataclass
class EvaluationOutcome:
    score: float
    passed: bool
    failure_explanation: Optional[str] = None
    details: Dict[str, Any] = None

    def __post_init__(self):
        if self.details is None:
            self.details = {}


# Lazy load SentenceTransformer to avoid heavy startup time
_EMBEDDING_MODEL = None


def get_embedding_model():
    global _EMBEDDING_MODEL
    if _EMBEDDING_MODEL is None:
        try:
            from sentence_transformers import SentenceTransformer
            _EMBEDDING_MODEL = SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True)
        except Exception:
            _EMBEDDING_MODEL = False
    return _EMBEDDING_MODEL


class ResponseEvaluator:
    @staticmethod
    def evaluate_exact_match(actual: str, expected: str) -> EvaluationOutcome:
        actual_clean = (actual or "").strip()
        expected_clean = (expected or "").strip()
        passed = actual_clean == expected_clean
        score = 1.0 if passed else 0.0
        explanation = None if passed else f"Expected exact match '{expected_clean}', got '{actual_clean}'"
        return EvaluationOutcome(score=score, passed=passed, failure_explanation=explanation)

    @staticmethod
    def normalize_text(text: str) -> str:
        if not text:
            return ""
        # Unicode normalization
        text = unicodedata.normalize("NFKD", text)
        # Lowercase
        text = text.lower()
        # Remove punctuation
        text = text.translate(str.maketrans("", "", string.punctuation))
        # Collapse whitespace
        text = re.sub(r"\s+", " ", text).strip()
        return text

    @classmethod
    def evaluate_normalized_text(cls, actual: str, expected: str) -> EvaluationOutcome:
        norm_actual = cls.normalize_text(actual)
        norm_expected = cls.normalize_text(expected)
        passed = norm_actual == norm_expected
        score = 1.0 if passed else 0.0
        explanation = None if passed else f"Normalized text mismatch: '{norm_actual}' != '{norm_expected}'"
        return EvaluationOutcome(
            score=score,
            passed=passed,
            failure_explanation=explanation,
            details={"normalized_actual": norm_actual, "normalized_expected": norm_expected},
        )

    @staticmethod
    def evaluate_keyword_validation(
        actual: str,
        required_keywords: Optional[List[str]] = None,
        forbidden_keywords: Optional[List[str]] = None,
    ) -> EvaluationOutcome:
        actual_lower = (actual or "").lower()
        req = required_keywords or []
        forb = forbidden_keywords or []

        missing_required = [k for k in req if k.lower() not in actual_lower]
        found_forbidden = [k for k in forb if k.lower() in actual_lower]

        passed = len(missing_required) == 0 and len(found_forbidden) == 0

        # Calculate score
        req_score = (len(req) - len(missing_required)) / len(req) if req else 1.0
        forb_penalty = (len(found_forbidden) / len(forb)) if forb else 0.0
        score = max(0.0, min(1.0, req_score - forb_penalty))

        explanations = []
        if missing_required:
            explanations.append(f"Missing required keywords: {missing_required}")
        if found_forbidden:
            explanations.append(f"Contains forbidden keywords: {found_forbidden}")

        return EvaluationOutcome(
            score=round(score, 4),
            passed=passed,
            failure_explanation="; ".join(explanations) if explanations else None,
            details={
                "missing_required": missing_required,
                "found_forbidden": found_forbidden,
            },
        )

    @classmethod
    def evaluate_semantic_similarity(
        cls,
        actual: str,
        expected: str,
        threshold: float = 0.8,
    ) -> EvaluationOutcome:
        if not actual or not expected:
            return EvaluationOutcome(
                score=0.0,
                passed=False,
                failure_explanation="Actual or expected response is empty for semantic comparison.",
            )

        model = get_embedding_model()
        if model and model is not False:
            try:
                embeddings = model.encode([actual, expected], convert_to_numpy=True)
                emb_actual, emb_expected = embeddings[0], embeddings[1]
                norm_a = np.linalg.norm(emb_actual)
                norm_e = np.linalg.norm(emb_expected)
                if norm_a > 0 and norm_e > 0:
                    cosine_sim = float(np.dot(emb_actual, emb_expected) / (norm_a * norm_e))
                else:
                    cosine_sim = 0.0
                score = max(0.0, min(1.0, cosine_sim))
            except Exception:
                score = cls._jaccard_fallback(actual, expected)
        else:
            score = cls._jaccard_fallback(actual, expected)

        score = round(score, 4)
        passed = score >= threshold
        explanation = (
            None
            if passed
            else f"Semantic similarity score {score:.4f} is below threshold {threshold:.4f}."
        )
        return EvaluationOutcome(
            score=score,
            passed=passed,
            failure_explanation=explanation,
            details={"threshold": threshold, "method": "sentence_transformers" if model else "token_overlap"},
        )

    @classmethod
    def _jaccard_fallback(cls, s1: str, s2: str) -> float:
        words1 = set(cls.normalize_text(s1).split())
        words2 = set(cls.normalize_text(s2).split())
        if not words1 or not words2:
            return 0.0
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        return float(len(intersection) / len(union))

    @staticmethod
    def evaluate_structured_json(
        actual: str,
        expected: Optional[str] = None,
        expected_schema: Optional[Dict[str, Any]] = None,
    ) -> EvaluationOutcome:
        # Extract json from potential markdown blocks ```json ... ```
        clean_text = actual.strip()
        json_match = re.search(r"```(?:json)?\s*(\{.*\}|\[.*\])\s*```", clean_text, re.DOTALL)
        if json_match:
            clean_text = json_match.group(1).strip()

        try:
            actual_data = json.loads(clean_text)
        except Exception as exc:
            return EvaluationOutcome(
                score=0.0,
                passed=False,
                failure_explanation=f"Output is not valid JSON: {exc}",
                details={"raw_output": actual},
            )

        # If expected is provided as a JSON string, compare contents
        if expected:
            try:
                expected_data = json.loads(expected)
                if actual_data == expected_data:
                    return EvaluationOutcome(score=1.0, passed=True, details={"matched_exact_json": True})
                # Check key overlap
                if isinstance(actual_data, dict) and isinstance(expected_data, dict):
                    expected_keys = set(expected_data.keys())
                    actual_keys = set(actual_data.keys())
                    missing = expected_keys - actual_keys
                    if missing:
                        return EvaluationOutcome(
                            score=0.5,
                            passed=False,
                            failure_explanation=f"JSON missing expected keys: {list(missing)}",
                            details={"missing_keys": list(missing)},
                        )
            except Exception:
                pass

        # If expected_schema is provided
        if expected_schema and isinstance(actual_data, dict):
            required_keys = expected_schema.get("required", [])
            missing_keys = [k for k in required_keys if k not in actual_data]
            if missing_keys:
                return EvaluationOutcome(
                    score=0.0,
                    passed=False,
                    failure_explanation=f"JSON failed schema validation. Missing required fields: {missing_keys}",
                    details={"missing_keys": missing_keys},
                )

        return EvaluationOutcome(
            score=1.0,
            passed=True,
            details={"parsed_json": actual_data},
        )

    @classmethod
    async def evaluate_llm_judge(
        cls,
        actual: str,
        input_prompt: str,
        expected: Optional[str] = None,
        judge_provider: Optional[Any] = None,
    ) -> EvaluationOutcome:
        if not judge_provider:
            # Deterministic heuristic fallback if judge provider not supplied
            outcome = cls.evaluate_semantic_similarity(actual, expected or input_prompt, threshold=0.7)
            return EvaluationOutcome(
                score=outcome.score,
                passed=outcome.passed,
                failure_explanation=outcome.failure_explanation,
                details={"judge_type": "heuristic_fallback"},
            )

        system_prompt = (
            "You are an expert AI evaluator. Assess the quality, correctness, and helpfulness "
            "of the agent's response given the user input and optional reference answer. "
            "Respond strictly in JSON with format: {\"score\": float 0.0-1.0, \"passed\": bool, \"explanation\": string}"
        )
        judge_input = (
            f"User Input: {input_prompt}\n"
            f"Expected Reference: {expected or 'N/A'}\n"
            f"Actual Response: {actual}\n"
        )

        try:
            response = await judge_provider.generate(judge_input, system_prompt=system_prompt)
            parsed = json.loads(response.text.strip())
            score = float(parsed.get("score", 0.0))
            passed = bool(parsed.get("passed", score >= 0.7))
            explanation = parsed.get("explanation", "")
            return EvaluationOutcome(
                score=score,
                passed=passed,
                failure_explanation=None if passed else explanation,
                details={"judge_model": getattr(judge_provider, "model_name", "unknown"), "judge_feedback": explanation},
            )
        except Exception as exc:
            return EvaluationOutcome(
                score=0.5,
                passed=False,
                failure_explanation=f"LLM judge evaluation failed: {exc}",
                details={"error": str(exc)},
            )
