import httpx
import pytest

from client.monitoring_client import MonitoringClient


def _mock_transport(routes: dict[str, tuple[int, dict]]) -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        method = request.method.upper()
        key = f"{method} {path}"
        for pattern, (status, body) in routes.items():
            if key == pattern:
                return httpx.Response(status, json=body)
        return httpx.Response(404, json={"detail": "Not found"})

    return httpx.MockTransport(handler)


TELEMETRY_RESPONSE = {
    "id": 1,
    "agent_id": 12,
    "timestamp": "2026-03-30T12:00:00Z",
    "latitude": 55.753,
    "longitude": 37.621,
    "battery_level": 41.5,
    "speed": 2.1,
    "link_status": "ONLINE",
    "mission_status": "IN_PROGRESS",
}

AGENT_STATUS_RESPONSE = {
    "agent_id": 12,
    "last_seen_at": "2026-03-30T12:00:00Z",
    "battery_level": 41.5,
    "link_status": "ONLINE",
    "health_state": "HEALTHY",
    "mission_status": "IN_PROGRESS",
}

ALERT_RESPONSE = {
    "id": 1,
    "agent_id": 12,
    "mission_id": None,
    "alert_type": "HUMAN_DETECTED",
    "severity": "HIGH",
    "message": "Survivor found",
    "created_at": "2026-03-30T12:00:00Z",
    "status": "ACTIVE",
}


@pytest.mark.asyncio
async def test_send_telemetry():
    transport = _mock_transport({"POST /api/v1/telemetry": (201, TELEMETRY_RESPONSE)})
    async with MonitoringClient(base_url="http://test") as c:
        c._client = httpx.AsyncClient(transport=transport, base_url="http://test")
        t = await c.send_telemetry(12, 55.753, 37.621, 41.5, 2.1, "ONLINE", "IN_PROGRESS")
        assert t.agent_id == 12
        assert t.battery_level == 41.5


@pytest.mark.asyncio
async def test_get_agent_status():
    transport = _mock_transport(
        {"GET /api/v1/agents/12/status": (200, AGENT_STATUS_RESPONSE)}
    )
    async with MonitoringClient(base_url="http://test") as c:
        c._client = httpx.AsyncClient(transport=transport, base_url="http://test")
        status = await c.get_agent_status(12)
        assert status.agent_id == 12
        assert status.health_state == "HEALTHY"


@pytest.mark.asyncio
async def test_get_available_agents():
    transport = _mock_transport(
        {"GET /api/v1/agents/available": (200, [AGENT_STATUS_RESPONSE])}
    )
    async with MonitoringClient(base_url="http://test") as c:
        c._client = httpx.AsyncClient(transport=transport, base_url="http://test")
        agents = await c.get_available_agents()
        assert len(agents) == 1
        assert agents[0].agent_id == 12


@pytest.mark.asyncio
async def test_create_alert():
    transport = _mock_transport({"POST /api/v1/alerts": (201, ALERT_RESPONSE)})
    async with MonitoringClient(base_url="http://test") as c:
        c._client = httpx.AsyncClient(transport=transport, base_url="http://test")
        alert = await c.create_alert(12, "HUMAN_DETECTED", "HIGH", "Survivor found")
        assert alert.alert_type == "HUMAN_DETECTED"


@pytest.mark.asyncio
async def test_get_alerts():
    transport = _mock_transport({"GET /api/v1/alerts": (200, [ALERT_RESPONSE])})
    async with MonitoringClient(base_url="http://test") as c:
        c._client = httpx.AsyncClient(transport=transport, base_url="http://test")
        alerts = await c.get_alerts()
        assert len(alerts) == 1


@pytest.mark.asyncio
async def test_health():
    transport = _mock_transport({"GET /health": (200, {"status": "ok"})})
    async with MonitoringClient(base_url="http://test") as c:
        c._client = httpx.AsyncClient(transport=transport, base_url="http://test")
        health = await c.health()
        assert health["status"] == "ok"


@pytest.mark.asyncio
async def test_client_not_open():
    c = MonitoringClient()
    with pytest.raises(RuntimeError, match="Client is not open"):
        _ = c.client
