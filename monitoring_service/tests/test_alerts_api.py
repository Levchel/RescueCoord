import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_alert(client: AsyncClient):
    payload = {
        "agent_id": 100,
        "alert_type": "HUMAN_DETECTED",
        "severity": "HIGH",
        "message": "Possible survivor detected by thermal camera",
    }
    resp = await client.post("/api/v1/alerts", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["agent_id"] == 100
    assert data["alert_type"] == "HUMAN_DETECTED"
    assert data["status"] == "ACTIVE"


@pytest.mark.asyncio
async def test_create_alert_with_mission(client: AsyncClient):
    payload = {
        "agent_id": 101,
        "mission_id": 1,
        "alert_type": "GAS_LEAK",
        "severity": "CRITICAL",
        "message": "Dangerous gas levels detected",
    }
    resp = await client.post("/api/v1/alerts", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["mission_id"] == 1


@pytest.mark.asyncio
async def test_list_alerts_empty(client: AsyncClient):
    resp = await client.get("/api/v1/alerts")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_list_alerts_filter_by_agent(client: AsyncClient):
    await client.post(
        "/api/v1/alerts",
        json={
            "agent_id": 200,
            "alert_type": "OBSTACLE",
            "severity": "LOW",
            "message": "Obstacle detected",
        },
    )
    await client.post(
        "/api/v1/alerts",
        json={
            "agent_id": 201,
            "alert_type": "FIRE",
            "severity": "CRITICAL",
            "message": "Fire detected",
        },
    )
    resp = await client.get("/api/v1/alerts", params={"agent_id": 200})
    data = resp.json()
    assert all(a["agent_id"] == 200 for a in data)


@pytest.mark.asyncio
async def test_list_alerts_filter_by_severity(client: AsyncClient):
    await client.post(
        "/api/v1/alerts",
        json={
            "agent_id": 300,
            "alert_type": "MALFUNCTION",
            "severity": "CRITICAL",
            "message": "Motor failure",
        },
    )
    resp = await client.get("/api/v1/alerts", params={"severity": "CRITICAL"})
    data = resp.json()
    assert all(a["severity"] == "CRITICAL" for a in data)
