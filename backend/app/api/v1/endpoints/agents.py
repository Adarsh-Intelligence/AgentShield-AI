from __future__ import annotations

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from backend.app.api.deps import verify_project_access
from backend.app.database.session import get_db
from backend.app.models.project import Project
from backend.app.schemas.agent import (
    AgentCreate,
    AgentResponse,
    AgentTestConnectionResponse,
    AgentUpdate,
)
from backend.app.services.agent_service import AgentService

router = APIRouter()


@router.post("/projects/{project_id}/agents", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
def create_agent(
    agent_in: AgentCreate,
    project: Project = Depends(verify_project_access),
    db: Session = Depends(get_db),
):
    """Register an external AI application with encrypted credentials and SSRF validation."""
    agent = AgentService.create_agent(db, project, agent_in)
    resp = AgentResponse.model_validate(agent)
    resp.has_api_key = bool(agent.credential)
    return resp


@router.get("/projects/{project_id}/agents", response_model=List[AgentResponse])
def get_agents(
    project: Project = Depends(verify_project_access),
    db: Session = Depends(get_db),
):
    """List all registered agents for a given project."""
    agents = AgentService.get_agents_by_project(db, project)
    result = []
    for a in agents:
        r = AgentResponse.model_validate(a)
        r.has_api_key = bool(a.credential)
        result.append(r)
    return result


@router.get("/projects/{project_id}/agents/{agent_id}", response_model=AgentResponse)
def get_agent(
    agent_id: str,
    project: Project = Depends(verify_project_access),
    db: Session = Depends(get_db),
):
    """Retrieve agent details."""
    agent = AgentService.get_agent_by_id(db, agent_id, project.id)
    resp = AgentResponse.model_validate(agent)
    resp.has_api_key = bool(agent.credential)
    return resp


@router.patch("/projects/{project_id}/agents/{agent_id}", response_model=AgentResponse)
def update_agent(
    agent_id: str,
    agent_in: AgentUpdate,
    project: Project = Depends(verify_project_access),
    db: Session = Depends(get_db),
):
    """Update agent configuration."""
    agent = AgentService.update_agent(db, agent_id, agent_in, project)
    resp = AgentResponse.model_validate(agent)
    resp.has_api_key = bool(agent.credential)
    return resp


@router.delete("/projects/{project_id}/agents/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_agent(
    agent_id: str,
    project: Project = Depends(verify_project_access),
    db: Session = Depends(get_db),
):
    """Delete registered agent."""
    AgentService.delete_agent(db, agent_id, project)


@router.post(
    "/projects/{project_id}/agents/{agent_id}/test-connection",
    response_model=AgentTestConnectionResponse,
)
async def test_agent_connection(
    agent_id: str,
    project: Project = Depends(verify_project_access),
    db: Session = Depends(get_db),
):
    """Test connectivity and authentication with external agent provider."""
    agent = AgentService.get_agent_by_id(db, agent_id, project.id)
    return await AgentService.test_agent_connection(agent)

