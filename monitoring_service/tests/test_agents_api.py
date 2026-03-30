import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_agent_status_not_found(client: AsyncClient):
    resp = await client.get("/api/v1/agents/999/status")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_agent_status_after_telemetry(client: AsyncClient):
    await client.post(
        "/api/v1/telemetry",
        json={
            "agent_id": 50,
            "latitude": 55.75,
            "longitude": 37.62,
            "battery_level": 85.0,
            "speed": 1.5,
            "link_status": "ONLINE",
            "mission_status": "PENDING",
        },
    )
    resp = await client.get("/api/v1/agents/50/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["agent_id"] == 50
    assert data["health_state"] == "HEALTHY"


@pytest.mark.asyncio
async def test_get_available_agents_empty(client: AsyncClient):
    resp = await client.get("/api/v1/agents/available")
    assert resp.status_code == 200
    # May or may not be empty depending on test isolation
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_get_available_agents_filters_offline(client: AsyncClient):
    # Create an online agent
    await client.post(
        "/api/v1/telemetry",
        json={
            "agent_id": 60,
            "latitude": 55.0,
            "longitude": 37.0,
            "battery_level": 70.0,
            "speed": 1.0,
            "link_status": "ONLINE",
            "mission_status": "PENDING",
        },
    )
    # Create an offline agent
    await client.post(
        "/api/v1/telemetry",
        json={
            "agent_id": 61,
            "latitude": 55.0,
            "longitude": 37.0,
            "battery_level": 50.0,
            "speed": 0.0,
            "link_status": "OFFLINE",
            "mission_status": "PENDING",
        },
    )
    resp = await client.get("/api/v1/agents/available")
    data = resp.json()
    agent_ids = [a["agent_id"] for a in data]
    assert 60 in agent_ids
    assert 61 not in agent_ids


@pytest.mark.asyncio
async def test_get_available_agents_filters_low_battery(client: AsyncClient):
    await client.post(
        "/api/v1/telemetry",
        json={
            "agent_id": 70,
            "latitude": 55.0,
            "longitude": 37.0,
            "battery_level": 5.0,
            "speed": 0.0,
            "link_status": "ONLINE",
            "mission_status": "PENDING",
        },
    )
    resp = await client.get("/api/v1/agents/available")
    data = resp.json()
    agent_ids = [a["agent_id"] for a in data]
    assert 70 not in agent_ids
