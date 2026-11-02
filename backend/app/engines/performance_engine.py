from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Tuple


# Configurable model pricing per 1,000,000 tokens (input, output) in USD
DEFAULT_MODEL_PRICING: Dict[str, Tuple[float, float]] = {
    # Groq models
    "llama3-70b-8192": (0.59, 0.79),
    "llama3-8b-8192": (0.05, 0.08),
    "mixtral-8x7b-32768": (0.24, 0.24),
    "gemma2-9b-it": (0.20, 0.20),
    # OpenAI models
    "gpt-4o": (5.00, 15.00),
    "gpt-4o-mini": (0.15, 0.60),
    # Ollama / Local
    "ollama": (0.0, 0.0),
    "mock-model": (0.0, 0.0),
}


@dataclass
class CalculatedMetrics:
    avg_latency_ms: float
    p50_latency_ms: float
    p95_latency_ms: float
    total_tokens: int
    prompt_tokens: int
    completion_tokens: int
    estimated_cost: float
    error_rate: float
    pass_rate: float


class PerformanceEngine:
    @staticmethod
    def calculate_percentile(data: List[float], percentile: float) -> float:
        if not data:
            return 0.0
        sorted_data = sorted(data)
        k = (len(sorted_data) - 1) * percentile
        f = math.floor(k)
        c = math.ceil(k)
        if f == c:
            return sorted_data[int(k)]
        d0 = sorted_data[int(f)] * (c - k)
        d1 = sorted_data[int(c)] * (k - f)
        return d0 + d1

    @classmethod
    def calculate_cost(
        cls,
        model_name: str,
        prompt_tokens: int,
        completion_tokens: int,
        custom_pricing: Dict[str, Tuple[float, float]] | None = None,
    ) -> float:
        pricing_table = custom_pricing or DEFAULT_MODEL_PRICING
        # Match model name or default
        matched = None
        for key, price in pricing_table.items():
            if key.lower() in model_name.lower():
                matched = price
                break
        if not matched:
            matched = (0.50, 1.50)  # Generic fallback estimate

        input_rate, output_rate = matched
        cost = (prompt_tokens / 1_000_000.0 * input_rate) + (completion_tokens / 1_000_000.0 * output_rate)
        return round(cost, 6)

    @classmethod
    def compute_metrics(
        cls,
        latencies_ms: List[float],
        passed_count: int,
        failed_count: int,
        prompt_tokens_list: List[int],
        completion_tokens_list: List[int],
        model_name: str = "mock-model",
    ) -> CalculatedMetrics:
        total_cases = passed_count + failed_count
        if total_cases == 0:
            return CalculatedMetrics(
                avg_latency_ms=0.0,
                p50_latency_ms=0.0,
                p95_latency_ms=0.0,
                total_tokens=0,
                prompt_tokens=0,
                completion_tokens=0,
                estimated_cost=0.0,
                error_rate=0.0,
                pass_rate=0.0,
            )

        avg_latency = float(sum(latencies_ms) / len(latencies_ms)) if latencies_ms else 0.0
        p50_latency = cls.calculate_percentile(latencies_ms, 0.50)
        p95_latency = cls.calculate_percentile(latencies_ms, 0.95)

        total_prompt_tokens = sum(prompt_tokens_list)
        total_completion_tokens = sum(completion_tokens_list)
        total_tokens = total_prompt_tokens + total_completion_tokens

        pass_rate = round(passed_count / total_cases, 4)
        error_rate = round(failed_count / total_cases, 4)

        estimated_cost = cls.calculate_cost(model_name, total_prompt_tokens, total_completion_tokens)

        return CalculatedMetrics(
            avg_latency_ms=round(avg_latency, 2),
            p50_latency_ms=round(p50_latency, 2),
            p95_latency_ms=round(p95_latency, 2),
            total_tokens=total_tokens,
            prompt_tokens=total_prompt_tokens,
            completion_tokens=total_completion_tokens,
            estimated_cost=estimated_cost,
            error_rate=error_rate,
            pass_rate=pass_rate,
        )

