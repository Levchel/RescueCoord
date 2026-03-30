from sqlalchemy import Column, Integer, Float, DateTime, Enum, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from .enums import LinkStatus, MissionStatus


class Base(DeclarativeBase):
    pass


class TelemetryRecord(Base):
    __tablename__ = "telemetry_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    agent_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    timestamp: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    battery_level: Mapped[float] = mapped_column(Float, nullable=False)
    speed: Mapped[float] = mapped_column(Float, nullable=False)
    link_status: Mapped[LinkStatus] = mapped_column(
        Enum(LinkStatus, name="link_status_enum"), nullable=False
    )
    mission_status: Mapped[MissionStatus] = mapped_column(
        Enum(MissionStatus, name="mission_status_enum"), nullable=False
    )
