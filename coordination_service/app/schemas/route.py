from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from ..models.enums import RouteStatus


class RouteResponse(BaseModel):
    id: int
    mission_id: int
    agent_id: int
    zone_id: int
    route_points: Optional[list] = None
    assigned_at: datetime
    route_status: RouteStatus

    model_config = {"from_attributes": True}


class RouteReassignRequest(BaseModel):
    new_agent_id: int
    reason: str
