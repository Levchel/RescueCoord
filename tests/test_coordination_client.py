import json

import httpx
import pytest
import pytest_asyncio

from client.coordination_client import CoordinationClient


def _mock_transport(routes: dict[str, tuple[int, dict]]) -> httpx.MockTransport:
    """Create a mock transport that returns predefined responses."""

    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        method = request.method.upper()
        key = f"{method} {path}"
        for pattern, (status, body) in routes.items():
            if key == pattern:
                return httpx.Response(status, json=body)
        return httpx.Response(404, json={"detail": "Not found"})

    return httpx.MockTransport(handler)


MISSION_RESPONSE = {
    "id": 1,
    "incident_type": "FIRE",
    "location": "Sector A",
    "priority": "HIGH",
    "created_at": "2026-03-30T12:00:00Z",
    "status": "CREATED",
    "required_agents": 3,
}

ZONE_RESPONSE = {
    "id": 1,
    "mission_id": 1,
    "zone_code": "ZONE-A",
    "geometry": None,
    "priority": "HIGH",
    "assigned_agent_id": 1,
    "status": "ASSIGNED",
}

ASSIGNMENT_RESPONSE = {
    "zone_code": "ZONE-A",
    "zone_id": 1,
    "agent_id": 1,
    "agent_name": "Agent-1",
    "route_id": 1,
    "route_status": "PLANNED",
}

REASSIGNMENT_RESPONSE = {
    "id": 1,
    "mission_id": 1,
    "from_agent_id": 1,
    "to_agent_id": 2,
    "reason": "Agent offline",
    "created_at": "2026-03-30T12:05:00Z",
}


@pytest.mark.asyncio
async def test_create_mission():
    transport = _mock_transport({"POST /api/v1/missions": (201, MISSION_RESPONSE)})
    async with CoordinationClient(base_url="http://test") as c:
        c._client = httpx.AsyncClient(transport=transport, base_url="http://test")
        mission = await c.create_mission("FIRE", "Sector A", "HIGH", 3)
        assert mission.id == 1
        assert mission.incident_type == "FIRE"


@pytest.mark.asyncio
async def test_get_mission():
    transport = _mock_transport({"GET /api/v1/missions/1": (200, MISSION_RESPONSE)})
    async with CoordinationClient(base_url="http://test") as c:
        c._client = httpx.AsyncClient(transport=transport, base_url="http://test")
        mission = await c.get_mission(1)
        assert mission.id == 1


@pytest.mark.asyncio
async def test_plan_mission():
    transport = _mock_transport(
        {"POST /api/v1/missions/1/plan": (200, [ZONE_RESPONSE])}
    )
    async with CoordinationClient(base_url="http://test") as c:
        c._client = httpx.AsyncClient(transport=transport, base_url="http://test")
        zones = await c.plan_mission(1)
        assert len(zones) == 1
        assert zones[0].zone_code == "ZONE-A"


@pytest.mark.asyncio
async def test_get_assignments():
    transport = _mock_transport(
        {"GET /api/v1/missions/1/assignments": (200, [ASSIGNMENT_RESPONSE])}
    )
    async with CoordinationClient(base_url="http://test") as c:
        c._client = httpx.AsyncClient(transport=transport, base_url="http://test")
        assignments = await c.get_assignments(1)
        assert len(assignments) == 1
        assert assignments[0].agent_name == "Agent-1"


@pytest.mark.asyncio
async def test_reassign_route():
    transport = _mock_transport(
        {"PATCH /api/v1/routes/1/reassign": (200, REASSIGNMENT_RESPONSE)}
    )
    async with CoordinationClient(base_url="http://test") as c:
        c._client = httpx.AsyncClient(transport=transport, base_url="http://test")
        result = await c.reassign_route(1, 2, "Agent offline")
        assert result.from_agent_id == 1
        assert result.to_agent_id == 2


@pytest.mark.asyncio
async def test_health():
    transport = _mock_transport({"GET /health": (200, {"status": "ok"})})
    async with CoordinationClient(base_url="http://test") as c:
        c._client = httpx.AsyncClient(transport=transport, base_url="http://test")
        health = await c.health()
        assert health["status"] == "ok"


@pytest.mark.asyncio
async def test_client_not_open():
    c = CoordinationClient()
    with pytest.raises(RuntimeError, match="Client is not open"):
        _ = c.client
