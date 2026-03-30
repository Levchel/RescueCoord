from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.mission import Mission
from ..models.enums import MissionStatusCoord
from ..schemas.mission import MissionCreate


async def create_mission(db: AsyncSession, data: MissionCreate) -> Mission:
    mission = Mission(
        incident_type=data.incident_type,
        location=data.location,
        priority=data.priority,
        required_agents=data.required_agents,
        status=MissionStatusCoord.CREATED,
    )
    db.add(mission)
    await db.commit()
    await db.refresh(mission)
    return mission


async def get_mission(db: AsyncSession, mission_id: int) -> Mission | None:
    result = await db.execute(
        select(Mission).where(Mission.id == mission_id)
    )
    return result.scalar_one_or_none()


async def update_mission_status(
    db: AsyncSession, mission_id: int, status: MissionStatusCoord
) -> Mission | None:
    mission = await get_mission(db, mission_id)
    if mission is None:
        return None
    mission.status = status
    await db.commit()
    await db.refresh(mission)
    return mission
