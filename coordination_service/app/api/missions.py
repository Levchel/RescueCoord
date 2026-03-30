from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models.mission import Mission
from ..models.search_zone import SearchZone
from ..models.route import Route
from ..schemas.mission import MissionCreate, MissionResponse, MissionDetailResponse
from ..schemas.search_zone import SearchZoneResponse
from ..schemas.task_reassignment import AssignmentResponse
from ..services import mission_service, planning_service

router = APIRouter(prefix="/api/v1", tags=["missions"])


@router.post("/missions", response_model=MissionResponse, status_code=status.HTTP_201_CREATED)
async def create_mission(data: MissionCreate, db: AsyncSession = Depends(get_db)):
    mission = await mission_service.create_mission(db, data)
    return mission


@router.get("/missions/{mission_id}", response_model=MissionDetailResponse)
async def get_mission(mission_id: int, db: AsyncSession = Depends(get_db)):
    mission = await mission_service.get_mission(db, mission_id)
    if mission is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mission not found")
    return mission


@router.post(
    "/missions/{mission_id}/plan",
    response_model=list[SearchZoneResponse],
    status_code=status.HTTP_200_OK,
)
async def plan_mission(mission_id: int, db: AsyncSession = Depends(get_db)):
    mission = await mission_service.get_mission(db, mission_id)
    if mission is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mission not found")
    zones = await planning_service.plan_mission(db, mission)
    return zones


@router.get("/missions/{mission_id}/assignments", response_model=list[AssignmentResponse])
async def get_assignments(mission_id: int, db: AsyncSession = Depends(get_db)):
    mission = await mission_service.get_mission(db, mission_id)
    if mission is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mission not found")

    result = await db.execute(
        select(SearchZone).where(SearchZone.mission_id == mission_id)
    )
    zones = result.scalars().all()

    assignments = []
    for zone in zones:
        # Find route for this zone
        route_result = await db.execute(
            select(Route).where(Route.zone_id == zone.id)
        )
        route = route_result.scalar_one_or_none()
        agent = zone.agent
        assignments.append(
            AssignmentResponse(
                zone_code=zone.zone_code,
                zone_id=zone.id,
                agent_id=zone.assigned_agent_id,
                agent_name=agent.name if agent else None,
                route_id=route.id if route else None,
                route_status=route.route_status.value if route else None,
            )
        )
    return assignments
