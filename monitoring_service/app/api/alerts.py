from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models.enums import AlertSeverity, AlertStatus
from ..schemas.alert import AlertCreate, AlertResponse
from ..services import alert_service

router = APIRouter(prefix="/api/v1", tags=["alerts"])


@router.post("/alerts", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
async def create_alert(data: AlertCreate, db: AsyncSession = Depends(get_db)):
    alert = await alert_service.create_alert(db, data)
    return alert


@router.get("/alerts", response_model=list[AlertResponse])
async def list_alerts(
    agent_id: Optional[int] = Query(None),
    mission_id: Optional[int] = Query(None),
    severity: Optional[AlertSeverity] = Query(None),
    status: Optional[AlertStatus] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    alerts = await alert_service.get_alerts(
        db, agent_id=agent_id, mission_id=mission_id, severity=severity, status=status
    )
    return alerts
