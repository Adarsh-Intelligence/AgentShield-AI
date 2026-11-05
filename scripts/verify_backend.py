import sys
import os
sys.path.insert(0, os.path.abspath("."))
import time
import httpx
import uvicorn
import threading

from backend.app.main import app

def run_server():
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="warning")

def test_backend():
    print("=" * 60)
    print("AgentShield AI — Live Backend Verification Suite")
    print("=" * 60)

    # Start server in daemon thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    time.sleep(2)  # Wait for Uvicorn to start

    base_url = "http://127.0.0.1:8001"
    client = httpx.Client(base_url=base_url, timeout=15.0)

    passed_checks = 0
    total_checks = 0

    def check(name, condition, details=""):
        nonlocal passed_checks, total_checks
        total_checks += 1
        if condition:
            passed_checks += 1
            print(f" [PASS] {name} {details}")
        else:
            print(f" [FAIL] {name} {details}")
            sys.exit(1)

    # 1. Health Probe
    res = client.get("/health")
    check("GET /health (Liveness)", res.status_code == 200 and res.json().get("status") == "healthy", f"status={res.status_code}")

    # 2. Ready Probe
    res = client.get("/ready")
    check("GET /ready (Readiness)", res.status_code == 200 and res.json().get("database") == "connected", f"status={res.status_code}")

    # 3. Prometheus Metrics
    res = client.get("/metrics")
    check("GET /metrics (Prometheus)", res.status_code == 200 and "agentshield_http_requests_total" in res.text, f"bytes={len(res.text)}")

    # 4. OpenAPI Specs & Docs
    res = client.get("/api/v1/openapi.json")
    check("GET /api/v1/openapi.json", res.status_code == 200 and "AgentShield AI" in res.text, f"routes={len(res.json().get('paths', {}))}")

    # 5. User Registration
    user_email = f"live_test_{int(time.time())}@agentshield.ai"
    res = client.post("/api/v1/auth/register", json={
        "email": user_email,
        "password": "LivePassword123!",
        "full_name": "Verification Engineer",
        "role": "developer"
    })
    check("POST /api/v1/auth/register", res.status_code == 201, f"user={user_email}")

    # 6. User Login (JWT generation)
    res = client.post("/api/v1/auth/login", json={
        "email": user_email,
        "password": "LivePassword123!"
    })
    token = res.json().get("access_token")
    refresh_token = res.json().get("refresh_token")
    check("POST /api/v1/auth/login", res.status_code == 200 and bool(token), f"token_len={len(token) if token else 0}")

    headers = {"Authorization": f"Bearer {token}"}

    # 7. Authenticated User Profile
    res = client.get("/api/v1/auth/me", headers=headers)
    check("GET /api/v1/auth/me", res.status_code == 200 and res.json().get("email") == user_email)

    # 8. Token Refresh
    res = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    check("POST /api/v1/auth/refresh", res.status_code == 200 and "access_token" in res.json())

    # 9. Create Project
    res = client.post("/api/v1/projects", headers=headers, json={
        "name": "Live Verification Project",
        "description": "End-to-end verification project",
        "config": {"mode": "strict"}
    })
    project_id = res.json().get("id")
    check("POST /api/v1/projects", res.status_code == 201 and bool(project_id), f"id={project_id}")

    # 10. Register AI Agent (Mock with encrypted credentials & SSRF check)
    res = client.post(f"/api/v1/projects/{project_id}/agents", headers=headers, json={
        "name": "Live Mock Agent",
        "provider_type": "mock",
        "api_endpoint": "http://mock.internal",
        "model_name": "mock-model",
        "api_key": "secret-live-verification-key",
        "timeout_seconds": 10
    })
    agent_id = res.json().get("id")
    check("POST /api/v1/projects/{id}/agents", res.status_code == 201 and res.json().get("has_api_key") is True, f"agent_id={agent_id}")

    # 11. Test Agent Connection
    res = client.post(f"/api/v1/projects/{project_id}/agents/{agent_id}/test-connection", headers=headers)
    check("POST /api/v1/projects/{id}/agents/{id}/test-connection", res.status_code == 200 and res.json().get("success") is True)

    # 12. Create Test Suite
    res = client.post(f"/api/v1/projects/{project_id}/test-suites", headers=headers, json={
        "name": "Verification Test Suite",
        "description": "Live Q&A verification suite"
    })
    suite_id = res.json().get("id")
    check("POST /api/v1/projects/{id}/test-suites", res.status_code == 201 and bool(suite_id), f"suite_id={suite_id}")

    # 13. Add Test Cases (Exact Match & Keyword Validation)
    res = client.post(f"/api/v1/projects/{project_id}/test-suites/{suite_id}/cases", headers=headers, json={
        "name": "Exact Match Greeting",
        "input_prompt": "Hello AgentShield",
        "expected_output": "Mock response from AgentShield AI",
        "evaluation_method": "exact_match"
    })
    check("POST /api/v1/.../cases (Exact Match)", res.status_code == 201)

    res = client.post(f"/api/v1/projects/{project_id}/test-suites/{suite_id}/cases", headers=headers, json={
        "name": "Keyword Enforcement",
        "input_prompt": "Status update",
        "expected_output": "Mock response from AgentShield AI",
        "evaluation_method": "keyword_validation",
        "required_keywords": ["AgentShield"],
        "forbidden_keywords": ["failure", "critical_error"]
    })
    check("POST /api/v1/.../cases (Keyword Validation)", res.status_code == 201)

    # 14. Execute Test Run (Synchronous Execution)
    res = client.post(f"/api/v1/projects/{project_id}/test-runs", headers=headers, json={
        "test_suite_id": suite_id,
        "agent_id": agent_id,
        "async_mode": False
    })
    run_data = res.json()
    run_id = run_data.get("id")
    check("POST /api/v1/projects/{id}/test-runs", res.status_code == 201 and run_data.get("status") == "completed", f"pass_rate={run_data.get('pass_rate')}")

    # 15. Retrieve Test Run Details
    res = client.get(f"/api/v1/projects/{project_id}/test-runs/{run_id}", headers=headers)
    results = res.json().get("results", [])
    check("GET /api/v1/projects/{id}/test-runs/{id}", res.status_code == 200 and len(results) == 2, f"results_count={len(results)}")

    # 16. Aggregate Performance Metrics
    res = client.get(f"/api/v1/projects/{project_id}/metrics", headers=headers)
    metrics = res.json()
    check("GET /api/v1/projects/{id}/metrics", res.status_code == 200 and metrics.get("total_evaluations") == 2, f"evals={metrics.get('total_evaluations')}")

    # 17. Security Scan (Prompt injection, synthetic secret & PII leakage)
    res = client.post(f"/api/v1/projects/{project_id}/security/scan", headers=headers, json={
        "agent_id": agent_id,
        "categories": ["prompt_injection", "sensitive_data_leakage"]
    })
    sec_data = res.json()
    check("POST /api/v1/projects/{id}/security/scan", res.status_code == 200 and "total_tests" in sec_data, f"scanned_tests={sec_data.get('total_tests')}")

    # 18. Standalone Ad-Hoc Evaluation Endpoint
    res = client.post("/api/v1/evaluations/evaluate", json={
        "actual_response": "The item was delivered on Tuesday.",
        "expected_response": "The item was delivered on Tuesday.",
        "evaluation_method": "exact_match"
    })
    check("POST /api/v1/evaluations/evaluate", res.status_code == 200 and res.json().get("passed") is True)

    # 19. Export Results CSV
    res = client.get(f"/api/v1/projects/{project_id}/test-runs/{run_id}/export-csv", headers=headers)
    check("GET /api/v1/.../export-csv", res.status_code == 200 and "Result ID,Test Case ID" in res.text, f"csv_bytes={len(res.text)}")

    print("=" * 60)
    print(f"RESULTS: {passed_checks}/{total_checks} CHECKS PASSED (100% OPERATIONAL)")
    print("=" * 60)

if __name__ == "__main__":
    test_backend()
