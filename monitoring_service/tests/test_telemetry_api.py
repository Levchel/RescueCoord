import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_post_telemetry(client: AsyncClient):
    payload = {
        "agent_id": 1,
        "latitude": 55.753,
        "longitude": 37.621,
        "battery_level": 80.0,
        "speed": 2.5,
        "link_status": "ONLINE",
        "mission_status": "IN_PROGRESS",
    }
    resp = await client.post("/api/v1/telemetry", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["agent_id"] == 1
    assert data["battery_level"] == 80.0
    assert data["link_status"] == "ONLINE"


@pytest.mark.asyncio
async def test_post_telemetry_creates_agent_status(client: AsyncClient):
    payload = {
        "agent_id": 10,
        "latitude": 55.0,
        "longitude": 37.0,
        "battery_level": 90.0,
        "speed": 1.0,
        "link_status": "ONLINE",
        "mission_status": "IN_PROGRESS",
    }
    resp = await client.post("/api/v1/telemetry", json=payload)
    assert resp.status_code == 201

    status_resp = await client.get("/api/v1/agents/10/status")
    assert status_resp.status_code == 200
    status = status_resp.json()
    assert status["agent_id"] == 10
    assert status["battery_level"] == 90.0
    assert status["health_state"] == "HEALTHY"


@pytest.mark.asyncio
async def test_low_battery_auto_alert(client: AsyncClient):
    payload = {
        "agent_id": 20,
        "latitude": 55.0,
        "longitude": 37.0,
        "battery_level": 10.0,
        "speed": 0.5,
        "link_status": "ONLINE",
        "mission_status": "IN_PROGRESS",
    }
    resp = await client.post("/api/v1/telemetry", json=payload)
    assert resp.status_code == 201

    alerts_resp = await client.get("/api/v1/alerts", params={"agent_id": 20})
    assert alerts_resp.status_code == 200
    alerts = alerts_resp.json()
    assert len(alerts) >= 1
    alert_types = [a["alert_type"] for a in alerts]
    assert "LOW_BATTERY" in alert_types


@pytest.mark.asyncio
async def test_link_lost_auto_alert(client: AsyncClient):
    payload = {
        "agent_id": 30,
        "latitude": 55.0,
        "longitude": 37.0,
        "battery_level": 50.0,
        "speed": 0.0,
        "link_status": "OFFLINE",
        "mission_status": "IN_PROGRESS",
    }
    resp = await client.post("/api/v1/telemetry", json=payload)
    assert resp.status_code == 201

    alerts_resp = await client.get("/api/v1/alerts", params={"agent_id": 30})
    alerts = alerts_resp.json()
    alert_types = [a["alert_type"] for a in alerts]
    assert "LINK_LOST" in alert_types


@pytest.mark.asyncio
async def test_post_telemetry_updates_agent_status(client: AsyncClient):
    # First telemetry
    await client.post(
        "/api/v1/telemetry",
        json={
            "agent_id": 40,
            "latitude": 55.0,
            "longitude": 37.0,
            "battery_level": 90.0,
            "speed": 3.0,
            "link_status": "ONLINE",
            "mission_status": "IN_PROGRESS",
        },
    )
    # Second telemetry with updated values
    await client.post(
        "/api/v1/telemetry",
        json={
            "agent_id": 40,
            "latitude": 55.1,
            "longitude": 37.1,
            "battery_level": 75.0,
            "speed": 2.0,
            "link_status": "DEGRADED",
            "mission_status": "IN_PROGRESS",
        },
    )
    status_resp = await client.get("/api/v1/agents/40/status")
    status = status_resp.json()
    assert status["battery_level"] == 75.0
    assert status["link_status"] == "DEGRADED"
    assert status["health_state"] == "WARNING"


@pytest.mark.asyncio
async def test_post_telemetry_validation_error(client: AsyncClient):
    payload = {
        "agent_id": 1,
        "latitude": 200.0,  # invalid
        "longitude": 37.0,
        "battery_level": 80.0,
        "speed": 1.0,
        "link_status": "ONLINE",
        "mission_status": "IN_PROGRESS",
    }
    resp = await client.post("/api/v1/telemetry", json=payload)
    assert resp.status_code == 422
