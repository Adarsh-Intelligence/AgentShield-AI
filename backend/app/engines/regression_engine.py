from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List
from backend.app.models.prompt import PromptVersion
from backend.app.models.test_run import TestRun
from backend.app.schemas.prompt import (
    PromptComparisonResponse,
    RegressionDetail,
)


class RegressionEngine:
    @staticmethod
    def compare_runs(
        baseline_run: TestRun,
        candidate_run: TestRun,
        baseline_prompt: PromptVersion,
        candidate_prompt: PromptVersion,
        pass_rate_tolerance: float = 0.0,
    ) -> PromptComparisonResponse:
        # Map test cases in baseline run
        baseline_results = {r.test_case_id: r for r in baseline_run.results}
        candidate_results = {r.test_case_id: r for r in candidate_run.results}

        all_case_ids = set(baseline_results.keys()).union(set(candidate_results.keys()))

        details: List[RegressionDetail] = []
        new_failures = 0
        resolved_failures = 0

        for case_id in all_case_ids:
            b_res = baseline_results.get(case_id)
            c_res = candidate_results.get(case_id)

            b_passed = b_res.passed if b_res else False
            c_passed = c_res.passed if c_res else False
            b_score = b_res.score if b_res else 0.0
            c_score = c_res.score if c_res else 0.0

            case_name = (
                (b_res.test_case.name if b_res and b_res.test_case else None)
                or (c_res.test_case.name if c_res and c_res.test_case else None)
                or f"Case {case_id[:8]}"
            )

            if b_passed and not c_passed:
                status = "REGRESSION"
                new_failures += 1
            elif not b_passed and c_passed:
                status = "IMPROVEMENT"
                resolved_failures += 1
            else:
                status = "UNCHANGED"

            details.append(
                RegressionDetail(
                    test_case_id=case_id,
                    test_case_name=case_name,
                    baseline_passed=b_passed,
                    candidate_passed=c_passed,
                    baseline_score=round(b_score, 4),
                    candidate_score=round(c_score, 4),
                    status=status,
                )
            )

        baseline_pass_rate = baseline_run.pass_rate
        candidate_pass_rate = candidate_run.pass_rate
        pass_rate_diff = round(candidate_pass_rate - baseline_pass_rate, 4)

        # A regression occurs if pass rate drop exceeds tolerance or if new failures are found
        is_regression = (pass_rate_diff < -pass_rate_tolerance) or (new_failures > 0)

        latency_diff = round(
            candidate_run.execution_duration_ms - baseline_run.execution_duration_ms, 2
        )

        b_metric = baseline_run.metrics
        c_metric = candidate_run.metrics
        token_diff = (c_metric.total_tokens - b_metric.total_tokens) if b_metric and c_metric else 0
        cost_diff = round((c_metric.estimated_cost - b_metric.estimated_cost), 6) if b_metric and c_metric else 0.0

        if is_regression:
            summary = (
                f"Regression detected! Candidate version '{candidate_prompt.version}' introduced {new_failures} "
                f"new failure(s). Pass rate changed by {pass_rate_diff * 100:.2f}%."
            )
        else:
            summary = (
                f"No regression detected. Candidate version '{candidate_prompt.version}' maintained or improved "
                f"performance ({resolved_failures} resolved failure(s))."
            )

        return PromptComparisonResponse(
            baseline_version=f"{baseline_prompt.name} ({baseline_prompt.version})",
            candidate_version=f"{candidate_prompt.name} ({candidate_prompt.version})",
            baseline_pass_rate=baseline_pass_rate,
            candidate_pass_rate=candidate_pass_rate,
            pass_rate_difference=pass_rate_diff,
            is_regression=is_regression,
            regression_summary=summary,
            new_failures_count=new_failures,
            resolved_failures_count=resolved_failures,
            latency_difference_ms=latency_diff,
            token_usage_difference=token_diff,
            cost_difference=cost_diff,
            details=details,
        )

