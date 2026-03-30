from sqlalchemy import Integer, String, Enum, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .mission import Base
from .enums import Priority, ZoneStatus


class SearchZone(Base):
    __tablename__ = "search_zones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    mission_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("missions.id"), nullable=False
    )
    zone_code: Mapped[str] = mapped_column(String(50), nullable=False)
    geometry: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    priority: Mapped[Priority] = mapped_column(
        Enum(Priority, name="priority_enum", create_constraint=False),
        nullable=False,
        default=Priority.MEDIUM,
    )
    assigned_agent_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("agents.id"), nullable=True
    )
    status: Mapped[ZoneStatus] = mapped_column(
        Enum(ZoneStatus, name="zone_status_enum"),
        nullable=False,
        default=ZoneStatus.PENDING,
    )

    mission = relationship("Mission", back_populates="zones")
    agent = relationship("Agent", lazy="selectin")
