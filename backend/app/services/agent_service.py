from __future__ import annotations

from typing import List, Optional
from sqlalchemy.orm import Session
from backend.app.core.exceptions import EntityNotFoundException
from backend.app.models.agent import Agent, AgentCredential
from backend.app.models.project import Project
from backend.app.providers.provider_factory import ProviderFactory
from backend.app.schemas.agent import (
    AgentCreate,
    AgentResponse,
    AgentTestConnectionResponse,
    AgentUpdate,
)
from backend.app.utils.encryption import encryption_service
from backend.app.utils.ssrf import validate_outbound_url


class AgentService:
    @staticmethod
    def create_agent(db: Session, project: Project, agent_in: AgentCreate) -> Agent:
        # Validate outbound URL against SSRF unless mock provider
        if agent_in.provider_type != "mock":
            validate_outbound_url(agent_in.api_endpoint)

        agent = Agent(
            project_id=project.id,
            name=agent_in.name,
            description=agent_in.description,
            provider_type=agent_in.provider_type,
            api_endpoint=agent_in.api_endpoint,
            model_name=agent_in.model_name,
            timeout_seconds=agent_in.timeout_seconds,
            custom_headers=agent_in.custom_headers or {},
            is_active=True,
        )
        db.add(agent)
        db.flush()

        # Encrypt API key if provided
        if agent_in.api_key:
            encrypted_key = encryption_service.encrypt(agent_in.api_key)
            credential = AgentCredential(
                agent_id=agent.id,
                encrypted_api_key=encrypted_key,
            )
            db.add(credential)

        db.commit()
        db.refresh(agent)
        return agent

    @staticmethod
    def get_agents_by_project(db: Session, project: Project) -> List[Agent]:
        return db.query(Agent).filter(Agent.project_id == project.id).all()

    @staticmethod
    def get_agent_by_id(db: Session, agent_id: str, project_id: Optional[str] = None) -> Agent:
        query = db.query(Agent).filter(Agent.id == agent_id)
        if project_id:
            query = query.filter(Agent.project_id == project_id)
        agent = query.first()
        if not agent:
            raise EntityNotFoundException("Agent", agent_id)
        return agent

    @staticmethod
    def update_agent(db: Session, agent_id: str, agent_in: AgentUpdate, project: Project) -> Agent:
        agent = AgentService.get_agent_by_id(db, agent_id, project.id)

        if agent_in.name is not None:
            agent.name = agent_in.name
        if agent_in.description is not None:
            agent.description = agent_in.description
        if agent_in.provider_type is not None:
            agent.provider_type = agent_in.provider_type
        if agent_in.api_endpoint is not None:
            if agent.provider_type != "mock":
                validate_outbound_url(agent_in.api_endpoint)
            agent.api_endpoint = agent_in.api_endpoint
        if agent_in.model_name is not None:
            agent.model_name = agent_in.model_name
        if agent_in.timeout_seconds is not None:
            agent.timeout_seconds = agent_in.timeout_seconds
        if agent_in.custom_headers is not None:
            agent.custom_headers = agent_in.custom_headers
        if agent_in.is_active is not None:
            agent.is_active = agent_in.is_active

        if agent_in.api_key is not None:
            encrypted_key = encryption_service.encrypt(agent_in.api_key)
            if agent.credential:
                agent.credential.encrypted_api_key = encrypted_key
            else:
                agent.credential = AgentCredential(
                    agent_id=agent.id,
                    encrypted_api_key=encrypted_key,
                )

        db.commit()
        db.refresh(agent)
        return agent

    @staticmethod
    def delete_agent(db: Session, agent_id: str, project: Project) -> None:
        agent = AgentService.get_agent_by_id(db, agent_id, project.id)
        db.delete(agent)
        db.commit()

    @staticmethod
    async def test_agent_connection(agent: Agent) -> AgentTestConnectionResponse:
        try:
            provider = ProviderFactory.get_provider_for_agent(agent)
            response = await provider.test_connection()
            return AgentTestConnectionResponse(
                success=True,
                provider_type=agent.provider_type,
                latency_ms=round(response.latency_ms, 2),
                message="Connection test successful.",
                raw_response=response.raw_response,
            )
        except Exception as exc:
            return AgentTestConnectionResponse(
                success=False,
                provider_type=agent.provider_type,
                latency_ms=0.0,
                message=f"Connection test failed: {exc}",
                raw_response={"error": str(exc)},
            )

