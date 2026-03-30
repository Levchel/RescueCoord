from sqlalchemy import Integer, String, DateTime, Enum, func
from sqlalchemy.orm import Mapped, mapped_column

from .telemetry import Base
from .enums import AlertType, AlertSeverity, AlertStatus


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    agent_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    mission_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    alert_type: Mapped[AlertType] = mapped_column(
        Enum(AlertType, name="alert_type_enum"), nullable=False
    )
    severity: Mapped[AlertSeverity] = mapped_column(
        Enum(AlertSeverity, name="alert_severity_enum"), nullable=False
    )
    message: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    status: Mapped[AlertStatus] = mapped_column(
        Enum(AlertStatus, name="alert_status_enum"),
        nullable=False,
        default=AlertStatus.ACTIVE,
    )
