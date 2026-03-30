from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.alert import Alert
from ..models.enums import AlertSeverity, AlertStatus
from ..schemas.alert import AlertCreate


async def create_alert(db: AsyncSession, data: AlertCreate) -> Alert:
    alert = Alert(
        agent_id=data.agent_id,
        mission_id=data.mission_id,
        alert_type=data.alert_type,
        severity=data.severity,
        message=data.message,
        status=AlertStatus.ACTIVE,
    )
    db.add(alert)
    await db.commit()
    await db.refresh(alert)
    return alert


async def get_alerts(
    db: AsyncSession,
    agent_id: Optional[int] = None,
    mission_id: Optional[int] = None,
    severity: Optional[AlertSeverity] = None,
    status: Optional[AlertStatus] = None,
) -> list[Alert]:
    query = select(Alert)
    if agent_id is not None:
        query = query.where(Alert.agent_id == agent_id)
    if mission_id is not None:
        query = query.where(Alert.mission_id == mission_id)
    if severity is not None:
        query = query.where(Alert.severity == severity)
    if status is not None:
        query = query.where(Alert.status == status)
    query = query.order_by(Alert.created_at.desc())
    result = await db.execute(query)
    return list(result.scalars().all())
