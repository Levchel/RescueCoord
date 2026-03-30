from sqlalchemy import Integer, DateTime, Enum, JSON, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .mission import Base
from .enums import RouteStatus


class Route(Base):
    __tablename__ = "routes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    mission_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("missions.id"), nullable=False
    )
    agent_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("agents.id"), nullable=False
    )
    zone_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("search_zones.id"), nullable=False
    )
    route_points: Mapped[list | None] = mapped_column(JSON, nullable=True)
    assigned_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    route_status: Mapped[RouteStatus] = mapped_column(
        Enum(RouteStatus, name="route_status_enum"),
        nullable=False,
        default=RouteStatus.PLANNED,
    )

    mission = relationship("Mission", back_populates="routes")
    agent = relationship("Agent", lazy="selectin")
    zone = relationship("SearchZone", lazy="selectin")
