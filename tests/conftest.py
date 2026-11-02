from __future__ import annotations

import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.config import settings
from backend.app.core.security import create_jwt_token, hash_password
from backend.app.database.base import Base
from backend.app.database.session import get_db
from backend.app.main import app
from backend.app.models.agent import Agent, AgentCredential
from backend.app.models.project import Project
from backend.app.models.test_case import TestCase
from backend.app.models.test_suite import TestSuite
from backend.app.models.user import User
from backend.app.utils.encryption import encryption_service

# Use in-memory SQLite database for test isolation
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db():
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def dev_user(db) -> User:
    user = User(
        email="developer@agentshield.ai",
        hashed_password=hash_password("DevPassword123!"),
        full_name="Alice Developer",
        role="developer",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def dev_user_2(db) -> User:
    user = User(
        email="developer2@agentshield.ai",
        hashed_password=hash_password("DevPassword123!"),
        full_name="Bob Developer",
        role="developer",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def admin_user(db) -> User:
    user = User(
        email="admin@agentshield.ai",
        hashed_password=hash_password("AdminPassword123!"),
        full_name="Super Admin",
        role="admin",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def auth_headers(dev_user) -> dict:
    token = create_jwt_token({"sub": dev_user.id, "email": dev_user.email, "role": dev_user.role})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers_dev2(dev_user_2) -> dict:
    token = create_jwt_token({"sub": dev_user_2.id, "email": dev_user_2.email, "role": dev_user_2.role})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(admin_user) -> dict:
    token = create_jwt_token({"sub": admin_user.id, "email": admin_user.email, "role": admin_user.role})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_project(db, dev_user) -> Project:
    project = Project(
        name="Support Bot Testing",
        description="Evaluation project for customer support AI",
        owner_id=dev_user.id,
        config={"threshold": 0.85},
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@pytest.fixture
def sample_mock_agent(db, sample_project) -> Agent:
    agent = Agent(
        project_id=sample_project.id,
        name="Support Mock Agent",
        description="Local mock LLM for testing",
        provider_type="mock",
        api_endpoint="http://mock-agent.local",
        model_name="mock-model",
        timeout_seconds=5,
        custom_headers={},
        is_active=True,
    )
    db.add(agent)
    db.flush()

    cred = AgentCredential(
        agent_id=agent.id,
        encrypted_api_key=encryption_service.encrypt("mock-api-key"),
    )
    db.add(cred)
    db.commit()
    db.refresh(agent)
    return agent

