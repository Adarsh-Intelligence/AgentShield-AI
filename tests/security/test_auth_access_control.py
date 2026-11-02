from __future__ import annotations

import pytest
from datetime import timedelta
from backend.app.core.security import create_jwt_token, revoke_token


class TestAuthAndAccessControl:
    def test_unauthenticated_request_rejected(self, client, sample_project):
        response = client.get(f"/api/v1/projects/{sample_project.id}")
        assert response.status_code == 401
        assert response.json()["error"]["code"] == "UNAUTHORIZED"

    def test_tampered_token_rejected(self, client, sample_project):
        fake_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalidpayload.invalidsig"
        response = client.get(
            f"/api/v1/projects/{sample_project.id}",
            headers={"Authorization": f"Bearer {fake_token}"},
        )
        assert response.status_code == 401

    def test_expired_token_rejected(self, client, sample_project, dev_user):
        # Create expired token
        expired_token = create_jwt_token(
            {"sub": dev_user.id, "email": dev_user.email, "role": dev_user.role},
            expires_delta=timedelta(seconds=-10),
        )
        response = client.get(
            f"/api/v1/projects/{sample_project.id}",
            headers={"Authorization": f"Bearer {expired_token}"},
        )
        assert response.status_code == 401
        assert "expired" in response.json()["error"]["message"].lower()

    def test_revoked_token_rejected(self, client, sample_project, dev_user):
        token = create_jwt_token({"sub": dev_user.id, "email": dev_user.email, "role": dev_user.role})
        revoke_token(token)
        response = client.get(
            f"/api/v1/projects/{sample_project.id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 401
        assert "revoked" in response.json()["error"]["message"].lower()

    def test_cross_tenant_project_isolation(self, client, sample_project, auth_headers_dev2):
        # dev_user owns sample_project; dev_user_2 tries to access it
        response = client.get(
            f"/api/v1/projects/{sample_project.id}",
            headers=auth_headers_dev2,
        )
        assert response.status_code == 403
        assert response.json()["error"]["code"] == "FORBIDDEN"

    def test_admin_can_access_any_project(self, client, sample_project, admin_headers):
        response = client.get(
            f"/api/v1/projects/{sample_project.id}",
            headers=admin_headers,
        )
        assert response.status_code == 200
        assert response.json()["id"] == sample_project.id

