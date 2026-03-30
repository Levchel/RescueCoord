import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_mission(client: AsyncClient):
    payload = {
        "incident_type": "BUILDING_COLLAPSE",
        "location": "Sector A",
        "priority": "HIGH",
        "required_agents": 3,
    }
    resp = await client.post("/api/v1/missions", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["incident_type"] == "BUILDING_COLLAPSE"
    assert data["location"] == "Sector A"
    assert data["priority"] == "HIGH"
    assert data["status"] == "CREATED"
    assert data["required_agents"] == 3


@pytest.mark.asyncio
async def test_get_mission(client: AsyncClient):
    # Create first
    create_resp = await client.post(
        "/api/v1/missions",
        json={
            "incident_type": "FIRE",
            "location": "Building B",
            "priority": "CRITICAL",
            "required_agents": 2,
        },
    )
    mission_id = create_resp.json()["id"]

    resp = await client.get(f"/api/v1/missions/{mission_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == mission_id
    assert data["incident_type"] == "FIRE"


@pytest.mark.asyncio
async def test_get_mission_not_found(client: AsyncClient):
    resp = await client.get("/api/v1/missions/99999")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_create_mission_validation(client: AsyncClient):
    payload = {
        "incident_type": "INVALID_TYPE",
        "location": "Sector A",
        "priority": "HIGH",
        "required_agents": 1,
    }
    resp = await client.post("/api/v1/missions", json=payload)
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_plan_mission(client: AsyncClient, mock_monitoring):
    # Create mission
    create_resp = await client.post(
        "/api/v1/missions",
        json={
            "incident_type": "BUILDING_COLLAPSE",
            "location": "Sector C",
            "priority": "HIGH",
            "required_agents": 3,
        },
    )
    mission_id = create_resp.json()["id"]

    # Plan mission
    plan_resp = await client.post(f"/api/v1/missions/{mission_id}/plan")
    assert plan_resp.status_code == 200
    zones = plan_resp.json()
    assert len(zones) == 3
    for zone in zones:
        assert zone["status"] == "ASSIGNED"
        assert zone["assigned_agent_id"] is not None

    # Verify mission status changed to IN_PROGRESS
    mission_resp = await client.get(f"/api/v1/missions/{mission_id}")
    assert mission_resp.json()["status"] == "IN_PROGRESS"


@pytest.mark.asyncio
async def test_get_assignments(client: AsyncClient, mock_monitoring):
    create_resp = await client.post(
        "/api/v1/missions",
        json={
            "incident_type": "FLOOD",
            "location": "River zone",
            "priority": "MEDIUM",
            "required_agents": 2,
        },
    )
    mission_id = create_resp.json()["id"]

    await client.post(f"/api/v1/missions/{mission_id}/plan")

    assignments_resp = await client.get(f"/api/v1/missions/{mission_id}/assignments")
    assert assignments_resp.status_code == 200
    assignments = assignments_resp.json()
    assert len(assignments) == 2
    for a in assignments:
        assert a["zone_code"] is not None
        assert a["agent_id"] is not None
        assert a["route_status"] == "PLANNED"


@pytest.mark.asyncio
async def test_plan_mission_not_found(client: AsyncClient):
    resp = await client.post("/api/v1/missions/99999/plan")
    assert resp.status_code == 404
