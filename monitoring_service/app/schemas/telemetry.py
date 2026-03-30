from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from ..models.enums import LinkStatus, MissionStatus


class TelemetryCreate(BaseModel):
    agent_id: int
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    battery_level: float = Field(..., ge=0, le=100)
    speed: float = Field(..., ge=0)
    link_status: LinkStatus
    mission_status: MissionStatus


class TelemetryResponse(BaseModel):
    id: int
    agent_id: int
    timestamp: datetime
    latitude: float
    longitude: float
    battery_level: float
    speed: float
    link_status: LinkStatus
    mission_status: MissionStatus

    model_config = {"from_attributes": True}
