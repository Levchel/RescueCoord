from typing import Optional

from pydantic import BaseModel, Field

from ..models.enums import AgentType, AvailabilityStatus


class AgentCreate(BaseModel):
    agent_type: AgentType
    name: str = Field(..., max_length=100)
    capabilities: Optional[dict] = None


class AgentResponse(BaseModel):
    id: int
    agent_type: AgentType
    name: str
    capabilities: Optional[dict] = None
    availability_status: AvailabilityStatus

    model_config = {"from_attributes": True}
