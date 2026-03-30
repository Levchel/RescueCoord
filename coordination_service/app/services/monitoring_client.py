from typing import Any

import httpx

from ..config import settings


class MonitoringClient:
    """HTTP client for calling the Monitoring Service API."""

    def __init__(self, base_url: str | None = None):
        self._base_url = (base_url or settings.MONITORING_SERVICE_URL).rstrip("/")

    async def get_available_agents(self) -> list[dict[str, Any]]:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{self._base_url}/api/v1/agents/available")
            resp.raise_for_status()
            return resp.json()

    async def get_agent_status(self, agent_id: int) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"{self._base_url}/api/v1/agents/{agent_id}/status"
            )
            resp.raise_for_status()
            return resp.json()


monitoring_client = MonitoringClient()
