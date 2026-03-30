from types import TracebackType
from typing import Optional

import httpx

from .models import (
    MissionModel,
    SearchZoneModel,
    AssignmentModel,
    TaskReassignmentModel,
)


class CoordinationClient:
    """Async Python SDK client for the Coordination Service."""

    def __init__(self, base_url: str = "http://localhost:8001"):
        self._base_url = base_url.rstrip("/")
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> "CoordinationClient":
        self._client = httpx.AsyncClient(base_url=self._base_url, timeout=30.0)
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            raise RuntimeError("Client is not open. Use 'async with CoordinationClient() as c:'")
        return self._client

    async def create_mission(
        self,
        incident_type: str,
        location: str,
        priority: str,
        required_agents: int = 1,
    ) -> MissionModel:
        resp = await self.client.post(
            "/api/v1/missions",
            json={
                "incident_type": incident_type,
                "location": location,
                "priority": priority,
                "required_agents": required_agents,
            },
        )
        resp.raise_for_status()
        return MissionModel(**resp.json())

    async def get_mission(self, mission_id: int) -> MissionModel:
        resp = await self.client.get(f"/api/v1/missions/{mission_id}")
        resp.raise_for_status()
        return MissionModel(**resp.json())

    async def plan_mission(self, mission_id: int) -> list[SearchZoneModel]:
        resp = await self.client.post(f"/api/v1/missions/{mission_id}/plan")
        resp.raise_for_status()
        return [SearchZoneModel(**z) for z in resp.json()]

    async def get_assignments(self, mission_id: int) -> list[AssignmentModel]:
        resp = await self.client.get(f"/api/v1/missions/{mission_id}/assignments")
        resp.raise_for_status()
        return [AssignmentModel(**a) for a in resp.json()]

    async def reassign_route(
        self, route_id: int, new_agent_id: int, reason: str
    ) -> TaskReassignmentModel:
        resp = await self.client.patch(
            f"/api/v1/routes/{route_id}/reassign",
            json={"new_agent_id": new_agent_id, "reason": reason},
        )
        resp.raise_for_status()
        return TaskReassignmentModel(**resp.json())

    async def health(self) -> dict:
        resp = await self.client.get("/health")
        resp.raise_for_status()
        return resp.json()
