from types import TracebackType
from typing import Optional

import httpx

from .models import AgentStatusModel, TelemetryModel, AlertModel


class MonitoringClient:
    """Async Python SDK client for the Monitoring Service."""

    def __init__(self, base_url: str = "http://localhost:8002"):
        self._base_url = base_url.rstrip("/")
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> "MonitoringClient":
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
            raise RuntimeError("Client is not open. Use 'async with MonitoringClient() as c:'")
        return self._client

    async def send_telemetry(
        self,
        agent_id: int,
        latitude: float,
        longitude: float,
        battery_level: float,
        speed: float,
        link_status: str,
        mission_status: str,
    ) -> TelemetryModel:
        resp = await self.client.post(
            "/api/v1/telemetry",
            json={
                "agent_id": agent_id,
                "latitude": latitude,
                "longitude": longitude,
                "battery_level": battery_level,
                "speed": speed,
                "link_status": link_status,
                "mission_status": mission_status,
            },
        )
        resp.raise_for_status()
        return TelemetryModel(**resp.json())

    async def get_agent_status(self, agent_id: int) -> AgentStatusModel:
        resp = await self.client.get(f"/api/v1/agents/{agent_id}/status")
        resp.raise_for_status()
        return AgentStatusModel(**resp.json())

    async def get_available_agents(self) -> list[AgentStatusModel]:
        resp = await self.client.get("/api/v1/agents/available")
        resp.raise_for_status()
        return [AgentStatusModel(**a) for a in resp.json()]

    async def create_alert(
        self,
        agent_id: int,
        alert_type: str,
        severity: str,
        message: str,
        mission_id: Optional[int] = None,
    ) -> AlertModel:
        payload: dict = {
            "agent_id": agent_id,
            "alert_type": alert_type,
            "severity": severity,
            "message": message,
        }
        if mission_id is not None:
            payload["mission_id"] = mission_id
        resp = await self.client.post("/api/v1/alerts", json=payload)
        resp.raise_for_status()
        return AlertModel(**resp.json())

    async def get_alerts(
        self,
        agent_id: Optional[int] = None,
        mission_id: Optional[int] = None,
        severity: Optional[str] = None,
        status: Optional[str] = None,
    ) -> list[AlertModel]:
        params: dict = {}
        if agent_id is not None:
            params["agent_id"] = agent_id
        if mission_id is not None:
            params["mission_id"] = mission_id
        if severity is not None:
            params["severity"] = severity
        if status is not None:
            params["status"] = status
        resp = await self.client.get("/api/v1/alerts", params=params)
        resp.raise_for_status()
        return [AlertModel(**a) for a in resp.json()]

    async def health(self) -> dict:
        resp = await self.client.get("/health")
        resp.raise_for_status()
        return resp.json()
