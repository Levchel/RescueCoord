from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.telemetry import TelemetryRecord
from ..models.agent_status import AgentStatus
from ..models.alert import Alert
from ..models.enums import (
    LinkStatus,
    HealthState,
    AlertType,
    AlertSeverity,
    AlertStatus,
    MissionStatus,
)
from ..schemas.telemetry import TelemetryCreate

LOW_BATTERY_THRESHOLD = 15.0


def _derive_health_state(battery: float, link: LinkStatus) -> HealthState:
    if link == LinkStatus.OFFLINE:
        return HealthState.OFFLINE
    if battery < LOW_BATTERY_THRESHOLD or link == LinkStatus.DEGRADED:
        return HealthState.WARNING
    if battery < 5.0:
        return HealthState.CRITICAL
    return HealthState.HEALTHY


async def save_telemetry(db: AsyncSession, data: TelemetryCreate) -> TelemetryRecord:
    now = datetime.now(timezone.utc)
    record = TelemetryRecord(
        agent_id=data.agent_id,
        timestamp=now,
        latitude=data.latitude,
        longitude=data.longitude,
        battery_level=data.battery_level,
        speed=data.speed,
        link_status=data.link_status,
        mission_status=data.mission_status,
    )
    db.add(record)

    # Upsert agent status
    health = _derive_health_state(data.battery_level, data.link_status)
    existing = await db.get(AgentStatus, data.agent_id)
    if existing:
        existing.last_seen_at = now
        existing.battery_level = data.battery_level
        existing.link_status = data.link_status
        existing.health_state = health
        existing.mission_status = data.mission_status
    else:
        agent_status = AgentStatus(
            agent_id=data.agent_id,
            last_seen_at=now,
            battery_level=data.battery_level,
            link_status=data.link_status,
            health_state=health,
            mission_status=data.mission_status,
        )
        db.add(agent_status)

    # Auto-generate alerts
    alerts: list[Alert] = []

    if data.battery_level < LOW_BATTERY_THRESHOLD:
        alerts.append(
            Alert(
                agent_id=data.agent_id,
                alert_type=AlertType.LOW_BATTERY,
                severity=AlertSeverity.HIGH
                if data.battery_level < 5.0
                else AlertSeverity.MEDIUM,
                message=f"Agent {data.agent_id}: battery level {data.battery_level}%",
                status=AlertStatus.ACTIVE,
            )
        )

    if data.link_status == LinkStatus.OFFLINE:
        alerts.append(
            Alert(
                agent_id=data.agent_id,
                alert_type=AlertType.LINK_LOST,
                severity=AlertSeverity.HIGH,
                message=f"Agent {data.agent_id}: link lost",
                status=AlertStatus.ACTIVE,
            )
        )

    for alert in alerts:
        db.add(alert)

    await db.commit()
    await db.refresh(record)
    return record


async def get_agent_status(db: AsyncSession, agent_id: int) -> AgentStatus | None:
    return await db.get(AgentStatus, agent_id)


async def get_available_agents(db: AsyncSession) -> list[AgentStatus]:
    result = await db.execute(
        select(AgentStatus).where(
            AgentStatus.health_state != HealthState.OFFLINE,
            AgentStatus.battery_level >= LOW_BATTERY_THRESHOLD,
        )
    )
    return list(result.scalars().all())
