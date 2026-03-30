"""
Integration test: full scenario using both services via TestClient.
Uses the Monitoring Service's real ASGI app directly and mocks
the monitoring HTTP call in the Coordination Service.
"""
import asyncio
from typing import AsyncGenerator
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# --- Monitoring Service setup ---
from monitoring_service.app.models.telemetry import Base as MonitoringBase
from monitoring_service.app.database import get_db as monitoring_get_db
from monitoring_service.app.main import app as monitoring_app

import monitoring_service.app.models.telemetry  # noqa
import monitoring_service.app.models.sensor_event  # noqa
import monitoring_service.app.models.alert  # noqa
import monitoring_service.app.models.agent_status  # noqa

# --- Coordination Service setup ---
from coordination_service.app.models.mission import Base as CoordinationBase
from coordination_service.app.database import get_db as coordination_get_db
from coordination_service.app.main import app as coordination_app

import coordination_service.app.models.mission  # noqa
import coordination_service.app.models.agent  # noqa
import coordination_service.app.models.search_zone  # noqa
import coordination_service.app.models.route  # noqa
import coordination_service.app.models.task_reassignment  # noqa


monitoring_engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
MonitoringSession = async_sessionmaker(monitoring_engine, class_=AsyncSession, expire_on_commit=False)

coordination_engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
CoordinationSession = async_sessionmaker(coordination_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(autouse=True)
async def setup_dbs():
    async with monitoring_engine.begin() as conn:
        await conn.run_sync(MonitoringBase.metadata.create_all)
    async with coordination_engine.begin() as conn:
        await conn.run_sync(CoordinationBase.metadata.create_all)
    yield
    async with monitoring_engine.begin() as conn:
        await conn.run_sync(MonitoringBase.metadata.drop_all)
    async with coordination_engine.begin() as conn:
        await conn.run_sync(CoordinationBase.metadata.drop_all)


async def override_monitoring_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with MonitoringSession() as session:
        yield session


async def override_coordination_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with CoordinationSession() as session:
        yield session


monitoring_app.dependency_overrides[monitoring_get_db] = override_monitoring_get_db
coordination_app.dependency_overrides[coordination_get_db] = override_coordination_get_db


@pytest_asyncio.fixture
async def monitoring_client():
    transport = ASGITransport(app=monitoring_app)
    async with AsyncClient(transport=transport, base_url="http://monitoring") as ac:
        yield ac


@pytest_asyncio.fixture
async def coordination_client():
    transport = ASGITransport(app=coordination_app)
    async with AsyncClient(transport=transport, base_url="http://coordination") as ac:
        yield ac


@pytest.mark.asyncio
async def test_full_scenario(monitoring_client: AsyncClient, coordination_client: AsyncClient):
    """
    Full integration scenario:
    1. Send telemetry from 3 agents to Monitoring Service
    2. Verify available agents
    3. Create a mission in Coordination Service
    4. Plan mission (mock the monitoring call using real monitoring data)
    5. Verify assignments
    6. Send low-battery telemetry → auto-alert
    7. Reassign route
    """

    # Step 1: Send telemetry for 3 agents
    for agent_id in [1, 2, 3]:
        resp = await monitoring_client.post(
            "/api/v1/telemetry",
            json={
                "agent_id": agent_id,
                "latitude": 55.75 + agent_id * 0.01,
                "longitude": 37.62 + agent_id * 0.01,
                "battery_level": 80.0 + agent_id,
                "speed": 2.0,
                "link_status": "ONLINE",
                "mission_status": "PENDING",
            },
        )
        assert resp.status_code == 201

    # Step 2: Check available agents
    avail_resp = await monitoring_client.get("/api/v1/agents/available")
    assert avail_resp.status_code == 200
    available = avail_resp.json()
    assert len(available) == 3

    # Step 3: Create mission
    mission_resp = await coordination_client.post(
        "/api/v1/missions",
        json={
            "incident_type": "BUILDING_COLLAPSE",
            "location": "Sector Alpha",
            "priority": "HIGH",
            "required_agents": 3,
        },
    )
    assert mission_resp.status_code == 201
    mission_id = mission_resp.json()["id"]

    # Step 4: Plan mission with mocked monitoring_client call
    with patch(
        "coordination_service.app.services.planning_service.monitoring_client"
    ) as mock_mc:
        mock_mc.get_available_agents = AsyncMock(return_value=available)
        plan_resp = await coordination_client.post(f"/api/v1/missions/{mission_id}/plan")
        assert plan_resp.status_code == 200
        zones = plan_resp.json()
        assert len(zones) == 3

    # Step 5: Verify assignments
    assign_resp = await coordination_client.get(
        f"/api/v1/missions/{mission_id}/assignments"
    )
    assert assign_resp.status_code == 200
    assignments = assign_resp.json()
    assert len(assignments) == 3

    # Step 6: Send low-battery telemetry → auto-alert
    resp = await monitoring_client.post(
        "/api/v1/telemetry",
        json={
            "agent_id": 1,
            "latitude": 55.76,
            "longitude": 37.63,
            "battery_level": 8.0,
            "speed": 0.5,
            "link_status": "ONLINE",
            "mission_status": "IN_PROGRESS",
        },
    )
    assert resp.status_code == 201

    alerts_resp = await monitoring_client.get(
        "/api/v1/alerts", params={"agent_id": 1}
    )
    alerts = alerts_resp.json()
    assert any(a["alert_type"] == "LOW_BATTERY" for a in alerts)

    # Step 7: Reassign route from agent 1 to agent 2
    route_id = assignments[0]["route_id"]
    reassign_resp = await coordination_client.patch(
        f"/api/v1/routes/{route_id}/reassign",
        json={
            "new_agent_id": 2,
            "reason": "Low battery on agent 1",
        },
    )
    assert reassign_resp.status_code == 200
    reassignment = reassign_resp.json()
    assert reassignment["to_agent_id"] == 2
    assert "Low battery" in reassignment["reason"]
