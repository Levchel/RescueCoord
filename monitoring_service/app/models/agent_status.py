from sqlalchemy import Integer, Float, DateTime, Enum, func
from sqlalchemy.orm import Mapped, mapped_column

from .telemetry import Base
from .enums import LinkStatus, HealthState, MissionStatus


class AgentStatus(Base):
    __tablename__ = "agent_status"

    agent_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    last_seen_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    battery_level: Mapped[float] = mapped_column(Float, nullable=False)
    link_status: Mapped[LinkStatus] = mapped_column(
        Enum(LinkStatus, name="link_status_enum", create_constraint=False),
        nullable=False,
    )
    health_state: Mapped[HealthState] = mapped_column(
        Enum(HealthState, name="health_state_enum"), nullable=False
    )
    mission_status: Mapped[MissionStatus] = mapped_column(
        Enum(MissionStatus, name="mission_status_enum", create_constraint=False),
        nullable=False,
    )
