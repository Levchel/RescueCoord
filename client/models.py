from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# --- Monitoring models ---

class AgentStatusModel(BaseModel):
    agent_id: int
    last_seen_at: datetime
    battery_level: float
    link_status: str
    health_state: str
    mission_status: str


class TelemetryModel(BaseModel):
    id: int
    agent_id: int
    timestamp: datetime
    latitude: float
    longitude: float
    battery_level: float
    speed: float
    link_status: str
    mission_status: str


class AlertModel(BaseModel):
    id: int
    agent_id: int
    mission_id: Optional[int] = None
    alert_type: str
    severity: str
    message: str
    created_at: datetime
    status: str


# --- Coordination models ---

class MissionModel(BaseModel):
    id: int
    incident_type: str
    location: str
    priority: str
    created_at: datetime
    status: str
    required_agents: int


class SearchZoneModel(BaseModel):
    id: int
    mission_id: int
    zone_code: str
    geometry: Optional[dict] = None
    priority: str
    assigned_agent_id: Optional[int] = None
    status: str


class RouteModel(BaseModel):
    id: int
    mission_id: int
    agent_id: int
    zone_id: int
    route_points: Optional[list] = None
    assigned_at: datetime
    route_status: str


class AssignmentModel(BaseModel):
    zone_code: str
    zone_id: int
    agent_id: Optional[int] = None
    agent_name: Optional[str] = None
    route_id: Optional[int] = None
    route_status: Optional[str] = None


class TaskReassignmentModel(BaseModel):
    id: int
    mission_id: int
    from_agent_id: int
    to_agent_id: int
    reason: str
    created_at: datetime
