from __future__ import annotations

import pytest


def test_full_platform_lifecycle_workflow(client):
    # 1. User Registration
    reg_resp = client.post(
        "/api/v1/auth/register",
        json={
            "email": "engineer@agentshield.ai",
            "password": "SecurePassword999!",
            "full_name": "Senior AI Engineer",
            "role": "developer",
        },
    )
    assert reg_resp.status_code == 201
    user_data = reg_resp.json()
    assert user_data["email"] == "engineer@agentshield.ai"

    # 2. Login
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": "engineer@agentshield.ai", "password": "SecurePassword999!"},
    )
    assert login_resp.status_code == 200
    token_data = login_resp.json()
    token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Check /me
    me_resp = client.get("/api/v1/auth/me", headers=headers)
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "engineer@agentshield.ai"

    # 4. Create Project
    proj_resp = client.post(
        "/api/v1/projects",
        json={
            "name": "Production Agent Guard",
            "description": "Project for auditing agent safety and regressions",
            "config": {"mode": "strict"},
        },
        headers=headers,
    )
    assert proj_resp.status_code == 201
    project_id = proj_resp.json()["id"]

    # 5. Register AI Agent
    agent_resp = client.post(
        f"/api/v1/projects/{project_id}/agents",
        json={
            "name": "Customer Support LLM",
            "description": "Production agent handling inquiries",
            "provider_type": "mock",
            "api_endpoint": "http://mock-agent.internal",
            "model_name": "mock-model",
            "api_key": "confidential-secret-api-key-999",
            "timeout_seconds": 10,
        },
        headers=headers,
    )
    assert agent_resp.status_code == 201
    agent_id = agent_resp.json()["id"]
    assert agent_resp.json()["has_api_key"] is True

    # 6. Test Agent Connection
    test_conn_resp = client.post(
        f"/api/v1/projects/{project_id}/agents/{agent_id}/test-connection",
        headers=headers,
    )
    assert test_conn_resp.status_code == 200
    assert test_conn_resp.json()["success"] is True

    # 7. Create Test Suite
    suite_resp = client.post(
        f"/api/v1/projects/{project_id}/test-suites",
        json={"name": "Core Q&A Suite", "description": "Verification of basic capabilities"},
        headers=headers,
    )
    assert suite_resp.status_code == 201
    suite_id = suite_resp.json()["id"]

    # Add Test Cases
    case1_resp = client.post(
        f"/api/v1/projects/{project_id}/test-suites/{suite_id}/cases",
        json={
            "name": "Greeting Validation",
            "input_prompt": "Hello",
            "expected_output": "Mock response from AgentShield AI",
            "evaluation_method": "exact_match",
        },
        headers=headers,
    )
    assert case1_resp.status_code == 201

    case2_resp = client.post(
        f"/api/v1/projects/{project_id}/test-suites/{suite_id}/cases",
        json={
            "name": "Keyword Check",
            "input_prompt": "What is this?",
            "expected_output": "Mock response from AgentShield AI",
            "evaluation_method": "keyword_validation",
            "required_keywords": ["AgentShield"],
            "forbidden_keywords": ["error", "malfunction"],
        },
        headers=headers,
    )
    assert case2_resp.status_code == 201

    # 8. Execute Test Run
    run_resp = client.post(
        f"/api/v1/projects/{project_id}/test-runs",
        json={"test_suite_id": suite_id, "agent_id": agent_id, "async_mode": False},
        headers=headers,
    )
    assert run_resp.status_code == 201
    run_data = run_resp.json()
    assert run_data["status"] == "completed"
    assert run_data["total_cases"] == 2
    assert run_data["passed_cases"] == 2
    assert run_data["pass_rate"] == 1.0

    run_id = run_data["id"]

    # 9. Get Test Run Details
    run_detail_resp = client.get(
        f"/api/v1/projects/{project_id}/test-runs/{run_id}",
        headers=headers,
    )
    assert run_detail_resp.status_code == 200
    assert len(run_detail_resp.json()["results"]) == 2

    # 10. Check Project Metrics
    metrics_resp = client.get(f"/api/v1/projects/{project_id}/metrics", headers=headers)
    assert metrics_resp.status_code == 200
    assert metrics_resp.json()["total_runs"] >= 1
    assert metrics_resp.json()["overall_pass_rate"] == 1.0

    # 11. Check Report and CSV Export
    reports_resp = client.get(f"/api/v1/projects/{project_id}/reports", headers=headers)
    assert reports_resp.status_code == 200
    assert len(reports_resp.json()) >= 1

    csv_resp = client.get(
        f"/api/v1/projects/{project_id}/test-runs/{run_id}/export-csv",
        headers=headers,
    )
    assert csv_resp.status_code == 200
    assert "Result ID,Test Case ID" in csv_resp.text

    # 12. Run Security Scan
    sec_resp = client.post(
        f"/api/v1/projects/{project_id}/security/scan",
        json={"agent_id": agent_id, "categories": ["prompt_injection", "sensitive_data_leakage"]},
        headers=headers,
    )
    assert sec_resp.status_code == 200
    assert "total_tests" in sec_resp.json()


def test_system_health_and_ready_endpoints(client):
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "healthy"

    ready = client.get("/ready")
    assert ready.status_code == 200
    assert ready.json()["database"] == "connected"

    metrics = client.get("/metrics")
    assert metrics.status_code == 200
    assert "agentshield_http_requests_total" in metrics.text

