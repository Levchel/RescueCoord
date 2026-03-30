from sqlalchemy import Column, Integer, String, DateTime, Enum, JSON, func
from sqlalchemy.orm import Mapped, mapped_column

from .telemetry import Base
from .enums import SensorType


class SensorEvent(Base):
    __tablename__ = "sensor_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    agent_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    timestamp: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    sensor_type: Mapped[SensorType] = mapped_column(
        Enum(SensorType, name="sensor_type_enum"), nullable=False
    )
    value: Mapped[dict] = mapped_column(JSON, nullable=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
