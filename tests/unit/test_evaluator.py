from __future__ import annotations

import pytest
from backend.app.engines.performance_engine import PerformanceEngine
from backend.app.engines.response_evaluator import ResponseEvaluator
from backend.app.engines.tool_evaluator import ToolEvaluator
from backend.app.providers.base import ToolCall


class TestResponseEvaluator:
    def test_exact_match_success(self):
        outcome = ResponseEvaluator.evaluate_exact_match("Hello world", "Hello world")
        assert outcome.passed is True
        assert outcome.score == 1.0
        assert outcome.failure_explanation is None

    def test_exact_match_failure(self):
        outcome = ResponseEvaluator.evaluate_exact_match("Hello World", "hello world")
        assert outcome.passed is False
        assert outcome.score == 0.0
        assert "Expected exact match" in outcome.failure_explanation

    def test_normalized_text_success(self):
        outcome = ResponseEvaluator.evaluate_normalized_text("Hello, World! ", "hello world")
        assert outcome.passed is True
        assert outcome.score == 1.0

    def test_keyword_validation_all_present(self):
        outcome = ResponseEvaluator.evaluate_keyword_validation(
            actual="The order has been shipped via FedEx tracking 12345.",
            required_keywords=["shipped", "tracking"],
            forbidden_keywords=["refund", "cancelled"],
        )
        assert outcome.passed is True
        assert outcome.score == 1.0

    def test_keyword_validation_forbidden_present(self):
        outcome = ResponseEvaluator.evaluate_keyword_validation(
            actual="Your order was cancelled and refunded.",
            required_keywords=["order"],
            forbidden_keywords=["cancelled"],
        )
        assert outcome.passed is False
        assert "Contains forbidden keywords" in outcome.failure_explanation

    def test_semantic_similarity_high(self):
        outcome = ResponseEvaluator.evaluate_semantic_similarity(
            actual="The weather in Paris is sunny and warm.",
            expected="Paris is experiencing warm and sunny weather.",
            threshold=0.6,
        )
        assert outcome.passed is True
        assert outcome.score >= 0.6

    def test_semantic_similarity_low(self):
        outcome = ResponseEvaluator.evaluate_semantic_similarity(
            actual="Quantum computing uses qubits and superposition.",
            expected="How to bake a chocolate cake in oven.",
            threshold=0.7,
        )
        assert outcome.passed is False
        assert outcome.score < 0.7

    def test_structured_json_valid_matching(self):
        actual_json = '{"name": "AgentShield", "status": "active", "version": 1}'
        expected_json = '{"name": "AgentShield", "status": "active", "version": 1}'
        outcome = ResponseEvaluator.evaluate_structured_json(actual_json, expected_json)
        assert outcome.passed is True
        assert outcome.score == 1.0

    def test_structured_json_missing_fields(self):
        actual_json = '{"status": "active"}'
        schema = {"required": ["status", "agent_id"]}
        outcome = ResponseEvaluator.evaluate_structured_json(
            actual_json, expected_schema=schema
        )
        assert outcome.passed is False
        assert "Missing required fields" in outcome.failure_explanation


class TestToolEvaluator:
    def test_tool_calling_correct_selection_and_arguments(self):
        actual = [ToolCall(name="get_weather", arguments={"city": "San Francisco", "unit": "celsius"})]
        expected = [{"name": "get_weather", "arguments": {"city": "San Francisco"}}]
        res = ToolEvaluator.evaluate(actual, expected)
        assert res.passed is True
        assert res.score == 1.0

    def test_tool_calling_unauthorized_dangerous_tool(self):
        actual = [ToolCall(name="bash_exec", arguments={"command": "rm -rf /"})]
        expected = [{"name": "get_weather", "arguments": {}}]
        res = ToolEvaluator.evaluate(actual, expected)
        assert res.passed is False
        assert "bash_exec" in res.unauthorized_tools

    def test_tool_calling_missing_expected_tool(self):
        actual = []
        expected = [{"name": "send_email", "arguments": {"recipient": "test@example.com"}}]
        res = ToolEvaluator.evaluate(actual, expected)
        assert res.passed is False
        assert "send_email" in res.failure_explanation


class TestPerformanceEngine:
    def test_compute_metrics_calculation(self):
        latencies = [100.0, 150.0, 200.0, 250.0, 300.0]
        metrics = PerformanceEngine.compute_metrics(
            latencies_ms=latencies,
            passed_count=4,
            failed_count=1,
            prompt_tokens_list=[100, 150, 200, 250, 300],
            completion_tokens_list=[50, 50, 50, 50, 50],
            model_name="llama3-70b-8192",
        )
        assert metrics.avg_latency_ms == 200.0
        assert metrics.p50_latency_ms == 200.0
        assert metrics.pass_rate == 0.8
        assert metrics.error_rate == 0.2
        assert metrics.total_tokens == 1250
        assert metrics.estimated_cost > 0.0

