from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from ..models.enums import IncidentType, Priority, MissionStatusCoord


class MissionCreate(BaseModel):
    incident_type: IncidentType
    location: str = Field(..., max_length=255)
    priority: Priority
    required_agents: int = Field(1, ge=1)


class MissionResponse(BaseModel):
    id: int
    incident_type: IncidentType
    location: str
    priority: Priority
    created_at: datetime
    status: MissionStatusCoord
    required_agents: int

    model_config = {"from_attributes": True}


class MissionDetailResponse(MissionResponse):
    zones: list["SearchZoneResponse"] = []
    routes: list["RouteResponse"] = []


from .search_zone import SearchZoneResponse  # noqa: E402
from .route import RouteResponse  # noqa: E402

MissionDetailResponse.model_rebuild()
