from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..schemas.agent_status import AgentStatusResponse
from ..services import telemetry_service

router = APIRouter(prefix="/api/v1", tags=["agents"])


@router.get("/agents/{agent_id}/status", response_model=AgentStatusResponse)
async def get_agent_status(agent_id: int, db: AsyncSession = Depends(get_db)):
    agent = await telemetry_service.get_agent_status(db, agent_id)
    if agent is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    return agent


@router.get("/agents/available", response_model=list[AgentStatusResponse])
async def get_available_agents(db: AsyncSession = Depends(get_db)):
    agents = await telemetry_service.get_available_agents(db)
    return agents
