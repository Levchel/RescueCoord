from typing import Optional

from pydantic import BaseModel

from ..models.enums import Priority, ZoneStatus


class SearchZoneResponse(BaseModel):
    id: int
    mission_id: int
    zone_code: str
    geometry: Optional[dict] = None
    priority: Priority
    assigned_agent_id: Optional[int] = None
    status: ZoneStatus

    model_config = {"from_attributes": True}
