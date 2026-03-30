from datetime import datetime

from pydantic import BaseModel


class TaskReassignmentResponse(BaseModel):
    id: int
    mission_id: int
    from_agent_id: int
    to_agent_id: int
    reason: str
    created_at: datetime

    model_config = {"from_attributes": True}


class AssignmentResponse(BaseModel):
    zone_code: str
    zone_id: int
    agent_id: int | None
    agent_name: str | None
    route_id: int | None
    route_status: str | None
