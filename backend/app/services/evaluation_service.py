from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from backend.app.core.exceptions import EntityNotFoundException
from backend.app.core.logging import EVALUATIONS_TOTAL, TEST_RUNS_TOTAL, logger
from backend.app.engines.performance_engine import PerformanceEngine
from backend.app.engines.response_evaluator import EvaluationOutcome, ResponseEvaluator
from backend.app.engines.tool_evaluator import ToolEvaluator
from backend.app.models.agent import Agent
from backend.app.models.metric import PerformanceMetric
from backend.app.models.prompt import PromptVersion
from backend.app.models.report import EvaluationReport
from backend.app.models.test_case import TestCase
from backend.app.models.test_result import TestResult
from backend.app.models.test_run import TestRun
from backend.app.models.test_suite import TestSuite
from backend.app.providers.provider_factory import ProviderFactory
from backend.app.schemas.evaluation import EvaluationRequest, EvaluationResultSchema


class EvaluationService:
    @staticmethod
    def evaluate_response_standalone(eval_req: EvaluationRequest) -> EvaluationResultSchema:
        method = eval_req.evaluation_method.lower()

        if method == "exact_match":
            outcome = ResponseEvaluator.evaluate_exact_match(
                eval_req.actual_response, eval_req.expected_response or ""
            )
        elif method == "normalized_text":
            outcome = ResponseEvaluator.evaluate_normalized_text(
                eval_req.actual_response, eval_req.expected_response or ""
            )
        elif method == "keyword_validation":
            outcome = ResponseEvaluator.evaluate_keyword_validation(
                eval_req.actual_response,
                eval_req.required_keywords,
                eval_req.forbidden_keywords,
            )
        elif method == "semantic_similarity":
            outcome = ResponseEvaluator.evaluate_semantic_similarity(
                eval_req.actual_response,
                eval_req.expected_response or "",
                threshold=eval_req.similarity_threshold or 0.8,
            )
        elif method == "structured_json":
            outcome = ResponseEvaluator.evaluate_structured_json(
                eval_req.actual_response,
                eval_req.expected_response,
                expected_schema=eval_req.expected_schema,
            )
        else:
            # Fallback
            outcome = ResponseEvaluator.evaluate_exact_match(
                eval_req.actual_response, eval_req.expected_response or ""
            )

        EVALUATIONS_TOTAL.labels(method=method, status="pass" if outcome.passed else "fail").inc()

        return EvaluationResultSchema(
            evaluation_method=method,
            score=outcome.score,
            passed=outcome.passed,
            failure_explanation=outcome.failure_explanation,
            details=outcome.details,
        )

    @classmethod
    async def execute_test_run(
        cls,
        db: Session,
        test_suite_id: str,
        agent_id: str,
        prompt_version_id: Optional[str] = None,
    ) -> TestRun:
        test_suite = db.query(TestSuite).filter(TestSuite.id == test_suite_id).first()
        if not test_suite:
            raise EntityNotFoundException("TestSuite", test_suite_id)

        agent = db.query(Agent).filter(Agent.id == agent_id).first()
        if not agent:
            raise EntityNotFoundException("Agent", agent_id)

        prompt_version = None
        if prompt_version_id:
            prompt_version = db.query(PromptVersion).filter(PromptVersion.id == prompt_version_id).first()

        # Initialize TestRun
        test_run = TestRun(
            test_suite_id=test_suite.id,
            agent_id=agent.id,
            prompt_version_id=prompt_version.id if prompt_version else None,
            status="running",
            started_at=datetime.now(timezone.utc),
            total_cases=len(test_suite.test_cases),
        )
        db.add(test_run)
        db.commit()
        db.refresh(test_run)

        provider = ProviderFactory.get_provider_for_agent(agent)

        run_start = time.perf_counter()
        latencies_ms: List[float] = []
        prompt_tokens_list: List[int] = []
        completion_tokens_list: List[int] = []
        passed_count = 0
        failed_count = 0

        try:
            for case in test_suite.test_cases:
                system_prompt = prompt_version.system_prompt if prompt_version else None
                user_prompt = case.input_prompt
                if prompt_version and prompt_version.user_template:
                    user_prompt = prompt_version.user_template.replace("{{input}}", user_prompt)

                case_start = time.perf_counter()
                provider_resp = await provider.generate(
                    prompt=user_prompt,
                    system_prompt=system_prompt,
                )
                case_duration_ms = (time.perf_counter() - case_start) * 1000.0

                latencies_ms.append(provider_resp.latency_ms or case_duration_ms)
                prompt_tokens_list.append(provider_resp.prompt_tokens)
                completion_tokens_list.append(provider_resp.completion_tokens)

                # Tool evaluation if test case expects tool calls
                tool_details = {}
                tool_passed = True
                tool_explanation = None
                if case.expected_tool_calls:
                    tool_eval = ToolEvaluator.evaluate(
                        actual_tool_calls=provider_resp.tool_calls,
                        expected_tool_calls=case.expected_tool_calls,
                    )
                    tool_passed = tool_eval.passed
                    tool_explanation = tool_eval.failure_explanation
                    tool_details = tool_eval.details

                # Response evaluation
                req = EvaluationRequest(
                    actual_response=provider_resp.text,
                    expected_response=case.expected_output,
                    evaluation_method=case.evaluation_method,
                    required_keywords=case.required_keywords,
                    forbidden_keywords=case.forbidden_keywords,
                    similarity_threshold=case.similarity_threshold,
                )
                eval_res = cls.evaluate_response_standalone(req)

                overall_passed = eval_res.passed and tool_passed
                if overall_passed:
                    passed_count += 1
                else:
                    failed_count += 1

                explanations = []
                if not eval_res.passed and eval_res.failure_explanation:
                    explanations.append(eval_res.failure_explanation)
                if not tool_passed and tool_explanation:
                    explanations.append(tool_explanation)

                cost = PerformanceEngine.calculate_cost(
                    agent.model_name,
                    provider_resp.prompt_tokens,
                    provider_resp.completion_tokens,
                )

                result_record = TestResult(
                    test_run_id=test_run.id,
                    test_case_id=case.id,
                    actual_response=provider_resp.text,
                    expected_response=case.expected_output,
                    evaluation_method=case.evaluation_method,
                    score=eval_res.score,
                    passed=overall_passed,
                    failure_explanation="; ".join(explanations) if explanations else None,
                    execution_duration_ms=round(case_duration_ms, 2),
                    prompt_tokens=provider_resp.prompt_tokens,
                    completion_tokens=provider_resp.completion_tokens,
                    total_tokens=provider_resp.total_tokens,
                    estimated_cost=cost,
                    tool_call_details=tool_details,
                )
                db.add(result_record)

            total_duration_ms = (time.perf_counter() - run_start) * 1000.0

            # Compute aggregate performance metrics
            metrics = PerformanceEngine.compute_metrics(
                latencies_ms=latencies_ms,
                passed_count=passed_count,
                failed_count=failed_count,
                prompt_tokens_list=prompt_tokens_list,
                completion_tokens_list=completion_tokens_list,
                model_name=agent.model_name,
            )

            metric_record = PerformanceMetric(
                test_run_id=test_run.id,
                agent_id=agent.id,
                avg_latency_ms=metrics.avg_latency_ms,
                p50_latency_ms=metrics.p50_latency_ms,
                p95_latency_ms=metrics.p95_latency_ms,
                total_tokens=metrics.total_tokens,
                prompt_tokens=metrics.prompt_tokens,
                completion_tokens=metrics.completion_tokens,
                estimated_cost=metrics.estimated_cost,
                error_rate=metrics.error_rate,
                pass_rate=metrics.pass_rate,
                metrics_breakdown={
                    "total_cases": len(test_suite.test_cases),
                    "passed_cases": passed_count,
                    "failed_cases": failed_count,
                },
            )
            db.add(metric_record)

            # Update test run
            test_run.status = "completed"
            test_run.completed_at = datetime.now(timezone.utc)
            test_run.passed_cases = passed_count
            test_run.failed_cases = failed_count
            test_run.pass_rate = metrics.pass_rate
            test_run.execution_duration_ms = round(total_duration_ms, 2)

            TEST_RUNS_TOTAL.labels(status="completed").inc()

            # Create default evaluation report
            report = EvaluationReport(
                project_id=test_suite.project_id,
                test_run_id=test_run.id,
                report_type="test_run",
                title=f"Evaluation Report: {test_suite.name} on {agent.name}",
                summary={
                    "total_cases": len(test_suite.test_cases),
                    "passed_cases": passed_count,
                    "failed_cases": failed_count,
                    "pass_rate": metrics.pass_rate,
                    "avg_latency_ms": metrics.avg_latency_ms,
                    "total_tokens": metrics.total_tokens,
                    "estimated_cost": metrics.estimated_cost,
                },
                content={
                    "suite_name": test_suite.name,
                    "agent_name": agent.name,
                    "model_name": agent.model_name,
                    "prompt_version": prompt_version.version if prompt_version else "default",
                },
            )
            db.add(report)

            db.commit()
            db.refresh(test_run)
            return test_run

        except Exception as exc:
            logger.error(f"Test run {test_run.id} failed: {exc}", exc_info=True)
            test_run.status = "failed"
            test_run.error_message = str(exc)
            test_run.completed_at = datetime.now(timezone.utc)
            TEST_RUNS_TOTAL.labels(status="failed").inc()
            db.commit()
            db.refresh(test_run)
            return test_run

