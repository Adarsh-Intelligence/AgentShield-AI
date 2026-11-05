# Repository audit (Phase 1, step 1)

Repository: `Adarsh-Intelligence/AgentShield-AI-v1`, audited at HEAD `726f132`
("feat: add interactive HTML landing page and documentation viewer on GET /").

## Scope of the audit — what was and was not read
Read line by line: `backend/app/engines/{security_engine,response_evaluator,performance_engine,tool_evaluator}.py`,
`backend/app/models/{metric,test_result}.py`, `backend/app/providers/base.py`,
the test-run loop in `backend/app/services/evaluation_service.py`, `backend/app/tasks/test_tasks.py`, `requirements.txt`.
Surveyed by file list / grep only: the remaining services, endpoints, schemas, migrations, tests, README claims.
Not run: the backend itself and its test suite (no database/Redis/Docker in the authoring environment).

## Findings that shape the ML work
1. **No ML exists in the repo** other than MiniLM similarity (below). No prompt-injection classifier, no anomaly detection, no `joblib` artifacts, no torch/transformers in `requirements.txt`.
2. **Semantic similarity already exists** in `ResponseEvaluator.evaluate_semantic_similarity`: `all-MiniLM-L6-v2`, cosine, **hard-coded default threshold 0.8**, with a **Jaccard token-overlap fallback** when the model cannot load.
   It sets `HF_HUB_OFFLINE=1` / `TRANSFORMERS_OFFLINE=1` and loads with `local_files_only=True`, so the model must already be in the local cache; otherwise it silently falls back to Jaccard (the result `details.method` says `token_overlap`).
   -> Phase 3 should *extend* this, using the calibrated threshold from Section 07 and an explicit model path, rather than add a second similarity module.
3. **Security scanning is output-side regex matching** (`SecurityEngine`): a fixed probe battery whose responses are checked against indicator patterns. There is no input-side classification of prompts. It also contains a weak indicator for unsafe tool use (`(?:exec|bash|shell|system)` matched against output text).
   -> The prompt-injection classifier would be a new input-side signal, kept *alongside* these deterministic checks.
4. **Telemetry that really exists** (per test case, `test_results`): `execution_duration_ms`, `prompt_tokens`, `completion_tokens`, `total_tokens`, `estimated_cost`, `passed`, `tool_call_details`. Per run (`performance_metrics`): avg/p50/p95 latency, token totals, `error_rate`, `pass_rate`.
   `tool_call_details` holds the observed tool calls **only when the test case declares expected tool calls**; otherwise it is `{}`.
5. **Telemetry that does not exist:** retry counts (no retry logic in the backend), request frequency, per-case error records (a provider exception inside the loop propagates and fails the whole run), failed tool-call counts (tools are never executed; only requested calls are observed).
   -> The PRD's features `retry_count`, `request_frequency`, `error_count`, `failed_tool_calls` are excluded from the anomaly model.
6. Existing tests: `tests/unit/test_evaluator.py`, `tests/security/test_security_engine.py`, integration tests. No tests cover ML.

## Decisions taken
- Everything ML lives under `ml/` (new). **No backend file was modified.**
- The PRD's proposed `ml/` layout was adopted as-is (no pre-existing equivalent folders to reuse).
- `ml/requirements-ml.txt` is separate from the backend `requirements.txt`; merging is a Phase 3 decision.
