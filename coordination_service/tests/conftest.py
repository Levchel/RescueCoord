import asyncio
from typing import AsyncGenerator
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.models.mission import Base
from app.database import get_db
from app.main import app as fastapi_app

# Import all models so they register with Base.metadata
import app.models.mission  # noqa: F401
import app.models.agent  # noqa: F401
import app.models.search_zone  # noqa: F401
import app.models.route  # noqa: F401
import app.models.task_reassignment  # noqa: F401

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        yield session


fastapi_app.dependency_overrides[get_db] = override_get_db


MOCK_AVAILABLE_AGENTS = [
    {
        "agent_id": 1,
        "last_seen_at": "2026-03-30T10:00:00Z",
        "battery_level": 85.0,
        "link_status": "ONLINE",
        "health_state": "HEALTHY",
        "mission_status": "PENDING",
    },
    {
        "agent_id": 2,
        "last_seen_at": "2026-03-30T10:00:00Z",
        "battery_level": 72.0,
        "link_status": "ONLINE",
        "health_state": "HEALTHY",
        "mission_status": "PENDING",
    },
    {
        "agent_id": 3,
        "last_seen_at": "2026-03-30T10:00:00Z",
        "battery_level": 60.0,
        "link_status": "ONLINE",
        "health_state": "HEALTHY",
        "mission_status": "PENDING",
    },
]


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def mock_monitoring():
    """Mock the monitoring_client that is used by planning_service."""
    with patch(
        "app.services.planning_service.monitoring_client"
    ) as mock_client:
        mock_client.get_available_agents = AsyncMock(return_value=MOCK_AVAILABLE_AGENTS)
        mock_client.get_agent_status = AsyncMock(
            return_value=MOCK_AVAILABLE_AGENTS[0]
        )
        yield mock_client
