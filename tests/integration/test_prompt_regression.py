from __future__ import annotations

import pytest


def test_prompt_versioning_and_regression_detection(client, sample_project, sample_mock_agent, auth_headers):
    project_id = sample_project.id
    agent_id = sample_mock_agent.id

    # 1. Create Prompt Version 1.0
    v1_resp = client.post(
        f"/api/v1/projects/{project_id}/prompts",
        json={
            "name": "CustomerSupportPrompt",
            "version": "v1.0",
            "system_prompt": "You are a professional customer support representative for AgentShield.",
            "description": "Baseline production prompt",
        },
        headers=auth_headers,
    )
    assert v1_resp.status_code == 201
    v1_id = v1_resp.json()["id"]
    assert v1_resp.json()["is_immutable"] is True

    # 2. Duplicate prompt version creation must fail (immutable uniqueness)
    dup_resp = client.post(
        f"/api/v1/projects/{project_id}/prompts",
        json={
            "name": "CustomerSupportPrompt",
            "version": "v1.0",
            "system_prompt": "Attempted override of immutable version",
        },
        headers=auth_headers,
    )
    assert dup_resp.status_code == 409

    # 3. Create Prompt Version 2.0
    v2_resp = client.post(
        f"/api/v1/projects/{project_id}/prompts",
        json={
            "name": "CustomerSupportPrompt",
            "version": "v2.0",
            "system_prompt": "You are a casual chatbot answering quick queries.",
            "description": "Candidate prompt for faster, informal responses",
        },
        headers=auth_headers,
    )
    assert v2_resp.status_code == 201
    v2_id = v2_resp.json()["id"]

    # 4. Create Test Suite
    suite_resp = client.post(
        f"/api/v1/projects/{project_id}/test-suites",
        json={"name": "Regression Test Suite"},
        headers=auth_headers,
    )
    suite_id = suite_resp.json()["id"]

    # Add test case
    client.post(
        f"/api/v1/projects/{project_id}/test-suites/{suite_id}/cases",
        json={
            "name": "Greeting Consistency",
            "input_prompt": "Hello",
            "expected_output": "Mock response from AgentShield AI",
            "evaluation_method": "exact_match",
        },
        headers=auth_headers,
    )

    # 5. Compare Prompt Versions (Baseline vs Candidate)
    compare_resp = client.post(
        f"/api/v1/projects/{project_id}/prompts/compare",
        json={
            "baseline_prompt_version_id": v1_id,
            "candidate_prompt_version_id": v2_id,
            "test_suite_id": suite_id,
            "agent_id": agent_id,
            "pass_rate_tolerance": 0.0,
        },
        headers=auth_headers,
    )
    assert compare_resp.status_code == 200
    comp_data = compare_resp.json()
    assert "baseline_version" in comp_data
    assert "candidate_version" in comp_data
    assert "is_regression" in comp_data
    assert "details" in comp_data
    assert len(comp_data["details"]) == 1

