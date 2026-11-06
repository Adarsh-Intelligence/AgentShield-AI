from __future__ import annotations

import os
import json
from typing import Dict, Any, Optional
from fastapi import APIRouter
from pydantic import BaseModel, Field
import joblib
import pandas as pd
import numpy as np

router = APIRouter(prefix="/ml", tags=["Machine Learning"])

# Lazy-loaded cached models
_PI_MODEL = None
_AD_MODEL = None
_AD_PREP = None
_PI_THRESHOLD = 0.14150592293851602


def get_pi_model():
    global _PI_MODEL, _PI_THRESHOLD
    if _PI_MODEL is None:
        model_path = os.path.abspath("ml/artifacts/prompt_injection/baseline_tfidf_lr.joblib")
        config_path = os.path.abspath("ml/artifacts/prompt_injection/config.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    _PI_THRESHOLD = cfg.get("models", {}).get("tfidf_lr", {}).get("threshold", 0.1415)
            except Exception:
                pass
        if os.path.exists(model_path):
            m = joblib.load(model_path)
            if hasattr(m, "named_steps") and "lr" in m.named_steps:
                setattr(m.named_steps["lr"], "multi_class", "ovr")
            _PI_MODEL = m
    return _PI_MODEL, _PI_THRESHOLD


def get_ad_models():
    global _AD_MODEL, _AD_PREP
    if _AD_MODEL is None or _AD_PREP is None:
        model_path = os.path.abspath("ml/artifacts/anomaly_detection/model.joblib")
        prep_path = os.path.abspath("ml/artifacts/anomaly_detection/preprocessing.joblib")
        if os.path.exists(model_path) and os.path.exists(prep_path):
            _AD_MODEL = joblib.load(model_path)
            p = joblib.load(prep_path)
            if hasattr(p, "steps") and len(p.steps) > 0:
                imp = p.steps[0][1]
                if hasattr(imp, "statistics_") and imp.statistics_ is not None:
                    imp.statistics_ = imp.statistics_.astype(float)
            _AD_PREP = p
    return _AD_MODEL, _AD_PREP


class PromptInjectionRequest(BaseModel):
    prompt: str = Field(..., description="The user prompt or context to evaluate for prompt injection.")


class PromptInjectionResponse(BaseModel):
    prompt: str
    score: float
    threshold: float
    is_malicious: bool
    classification: str
    model: str = "tfidf_lr (BIPIA baseline)"


class TelemetryAnomalyRequest(BaseModel):
    latency_ms: float = 350.0
    prompt_tokens: float = 120.0
    completion_tokens: float = 100.0
    tool_call_count: float = 1.0
    unauthorized_tool_count: float = 0.0


class TelemetryAnomalyResponse(BaseModel):
    is_anomaly: bool
    status: str
    features: Dict[str, float]
    model: str = "IsolationForest (synthetic telemetry)"


@router.get("/info")
def get_ml_info() -> Dict[str, Any]:
    """Retrieve metadata about the installed ML models and datasets."""
    manifest_path = os.path.abspath("ml/artifacts/manifest.json")
    if os.path.exists(manifest_path):
        with open(manifest_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"status": "available", "version": "0.1.0"}


@router.post("/classify-injection", response_model=PromptInjectionResponse)
def classify_prompt_injection(req: PromptInjectionRequest):
    """Classify whether a prompt contains prompt injection using the TF-IDF LR model."""
    model, threshold = get_pi_model()
    if model is None:
        return PromptInjectionResponse(
            prompt=req.prompt,
            score=0.0,
            threshold=threshold,
            is_malicious=False,
            classification="MODEL_NOT_FOUND"
        )

    prob = float(model.predict_proba([req.prompt])[0, 1])
    is_malicious = prob >= threshold
    return PromptInjectionResponse(
        prompt=req.prompt,
        score=round(prob, 4),
        threshold=round(threshold, 4),
        is_malicious=is_malicious,
        classification="MALICIOUS" if is_malicious else "SAFE"
    )


@router.post("/detect-anomaly", response_model=TelemetryAnomalyResponse)
def detect_telemetry_anomaly(req: TelemetryAnomalyRequest):
    """Detect telemetry anomalies (latency, token spikes, tool storms) using Isolation Forest."""
    ad_model, ad_prep = get_ad_models()
    ratio = req.completion_tokens / (req.prompt_tokens + 1.0)
    features = {
        "latency_ms": req.latency_ms,
        "prompt_tokens": req.prompt_tokens,
        "completion_tokens": req.completion_tokens,
        "completion_prompt_ratio": ratio,
        "tool_call_count": req.tool_call_count,
        "unauthorized_tool_count": req.unauthorized_tool_count
    }

    if ad_model is None or ad_prep is None:
        return TelemetryAnomalyResponse(
            is_anomaly=False,
            status="MODEL_NOT_FOUND",
            features=features
        )

    df = pd.DataFrame([features])[ad_prep.steps[0][1].feature_names_in_].astype(float)
    scaled = ad_prep.transform(df)
    pred = int(ad_model.predict(scaled)[0])  # 1 = Normal, -1 = Anomaly
    is_anomaly = pred == -1

    return TelemetryAnomalyResponse(
        is_anomaly=is_anomaly,
        status="ANOMALY" if is_anomaly else "NORMAL",
        features=features
    )

