from sqlalchemy import Integer, String, DateTime, Enum, JSON, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from .enums import IncidentType, Priority, MissionStatusCoord


class Base(DeclarativeBase):
    pass


class Mission(Base):
    __tablename__ = "missions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    incident_type: Mapped[IncidentType] = mapped_column(
        Enum(IncidentType, name="incident_type_enum"), nullable=False
    )
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    priority: Mapped[Priority] = mapped_column(
        Enum(Priority, name="priority_enum"), nullable=False
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    status: Mapped[MissionStatusCoord] = mapped_column(
        Enum(MissionStatusCoord, name="mission_status_coord_enum"),
        nullable=False,
        default=MissionStatusCoord.CREATED,
    )
    required_agents: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    zones = relationship("SearchZone", back_populates="mission", lazy="selectin")
    routes = relationship("Route", back_populates="mission", lazy="selectin")
