import math
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.mission import Mission
from ..models.agent import Agent
from ..models.search_zone import SearchZone
from ..models.route import Route
from ..models.enums import (
    MissionStatusCoord,
    AvailabilityStatus,
    ZoneStatus,
    RouteStatus,
    Priority,
)
from .monitoring_client import monitoring_client


async def _ensure_agents_in_db(
    db: AsyncSession, remote_agents: list[dict[str, Any]]
) -> list[Agent]:
    """Ensure agents from the Monitoring Service exist in the local DB."""
    agents = []
    for ra in remote_agents:
        agent_id = ra["agent_id"]
        existing = await db.get(Agent, agent_id)
        if existing is None:
            existing = Agent(
                id=agent_id,
                agent_type="GROUND_ROBOT",
                name=f"Agent-{agent_id}",
                availability_status=AvailabilityStatus.AVAILABLE,
            )
            db.add(existing)
        else:
            existing.availability_status = AvailabilityStatus.AVAILABLE
        agents.append(existing)
    await db.flush()
    return agents


def _generate_grid_zones(
    num_zones: int, base_lat: float = 55.75, base_lon: float = 37.62, step: float = 0.005
) -> list[dict]:
    """Generate a simple grid of zones around a base coordinate."""
    cols = math.ceil(math.sqrt(num_zones))
    zones = []
    for i in range(num_zones):
        row, col = divmod(i, cols)
        lat_min = base_lat + row * step
        lon_min = base_lon + col * step
        zones.append(
            {
                "zone_code": f"ZONE-{chr(65 + i)}",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [lon_min, lat_min],
                        [lon_min + step, lat_min],
                        [lon_min + step, lat_min + step],
                        [lon_min, lat_min + step],
                        [lon_min, lat_min],
                    ],
                },
            }
        )
    return zones


def _generate_route_points(geometry: dict) -> list:
    """Generate waypoints from zone geometry (simplified patrol path)."""
    coords = geometry.get("coordinates", [])
    if len(coords) >= 4:
        return coords[:4]
    return coords


async def plan_mission(db: AsyncSession, mission: Mission) -> list[SearchZone]:
    """Fetch available agents from Monitoring, split zones, assign agents."""
    mission.status = MissionStatusCoord.PLANNING
    await db.flush()

    # Fetch available agents from Monitoring Service
    remote_agents = await monitoring_client.get_available_agents()

    # Limit to required agents count
    needed = min(mission.required_agents, len(remote_agents))
    if needed == 0:
        mission.status = MissionStatusCoord.CREATED
        await db.commit()
        return []

    remote_agents = remote_agents[:needed]
    agents = await _ensure_agents_in_db(db, remote_agents)

    # Remove old zones/routes for this mission (re-planning)
    old_zones = await db.execute(
        select(SearchZone).where(SearchZone.mission_id == mission.id)
    )
    for z in old_zones.scalars().all():
        await db.delete(z)
    old_routes = await db.execute(
        select(Route).where(Route.mission_id == mission.id)
    )
    for r in old_routes.scalars().all():
        await db.delete(r)
    await db.flush()

    # Generate zones
    zone_data = _generate_grid_zones(needed)
    created_zones = []
    for i, zd in enumerate(zone_data):
        zone = SearchZone(
            mission_id=mission.id,
            zone_code=zd["zone_code"],
            geometry=zd["geometry"],
            priority=mission.priority,
            assigned_agent_id=agents[i].id,
            status=ZoneStatus.ASSIGNED,
        )
        db.add(zone)
        created_zones.append(zone)
    await db.flush()

    # Create routes
    for i, zone in enumerate(created_zones):
        route = Route(
            mission_id=mission.id,
            agent_id=agents[i].id,
            zone_id=zone.id,
            route_points=_generate_route_points(zone.geometry),
            route_status=RouteStatus.PLANNED,
        )
        db.add(route)

    # Mark agents as busy
    for agent in agents:
        agent.availability_status = AvailabilityStatus.BUSY

    mission.status = MissionStatusCoord.IN_PROGRESS
    await db.commit()

    # Refresh zones to include IDs
    for zone in created_zones:
        await db.refresh(zone)

    return created_zones
