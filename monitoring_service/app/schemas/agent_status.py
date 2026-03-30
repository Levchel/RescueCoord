from datetime import datetime

from pydantic import BaseModel

from ..models.enums import LinkStatus, HealthState, MissionStatus


class AgentStatusResponse(BaseModel):
    agent_id: int
    last_seen_at: datetime
    battery_level: float
    link_status: LinkStatus
    health_state: HealthState
    mission_status: MissionStatus

    model_config = {"from_attributes": True}
