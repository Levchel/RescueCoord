import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_reassign_route(client: AsyncClient, mock_monitoring):
    # Create and plan a mission
    create_resp = await client.post(
        "/api/v1/missions",
        json={
            "incident_type": "INDUSTRIAL_ACCIDENT",
            "location": "Factory zone",
            "priority": "HIGH",
            "required_agents": 2,
        },
    )
    mission_id = create_resp.json()["id"]
    await client.post(f"/api/v1/missions/{mission_id}/plan")

    # Get assignments to find a route ID
    assignments_resp = await client.get(f"/api/v1/missions/{mission_id}/assignments")
    assignments = assignments_resp.json()
    route_id = assignments[0]["route_id"]
    old_agent_id = assignments[0]["agent_id"]

    # Pick a different agent
    new_agent_id = assignments[1]["agent_id"]

    resp = await client.patch(
        f"/api/v1/routes/{route_id}/reassign",
        json={"new_agent_id": new_agent_id, "reason": "Agent unresponsive"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["from_agent_id"] == old_agent_id
    assert data["to_agent_id"] == new_agent_id
    assert data["reason"] == "Agent unresponsive"


@pytest.mark.asyncio
async def test_reassign_route_not_found(client: AsyncClient):
    resp = await client.patch(
        "/api/v1/routes/99999/reassign",
        json={"new_agent_id": 1, "reason": "Test"},
    )
    assert resp.status_code == 404
