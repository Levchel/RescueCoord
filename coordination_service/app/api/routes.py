from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models.route import Route
from ..models.task_reassignment import TaskReassignment
from ..models.enums import RouteStatus, AvailabilityStatus
from ..schemas.route import RouteResponse, RouteReassignRequest
from ..schemas.task_reassignment import TaskReassignmentResponse

router = APIRouter(prefix="/api/v1", tags=["routes"])


@router.patch("/routes/{route_id}/reassign", response_model=TaskReassignmentResponse)
async def reassign_route(
    route_id: int,
    data: RouteReassignRequest,
    db: AsyncSession = Depends(get_db),
):
    route = await db.get(Route, route_id)
    if route is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route not found")

    old_agent_id = route.agent_id

    # Update route
    route.route_status = RouteStatus.REASSIGNED
    new_route = Route(
        mission_id=route.mission_id,
        agent_id=data.new_agent_id,
        zone_id=route.zone_id,
        route_points=route.route_points,
        route_status=RouteStatus.PLANNED,
    )
    db.add(new_route)

    # Update zone assignment
    zone = route.zone
    if zone:
        zone.assigned_agent_id = data.new_agent_id

    # Record reassignment
    reassignment = TaskReassignment(
        mission_id=route.mission_id,
        from_agent_id=old_agent_id,
        to_agent_id=data.new_agent_id,
        reason=data.reason,
    )
    db.add(reassignment)

    await db.commit()
    await db.refresh(reassignment)
    return reassignment
