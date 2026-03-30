from sqlalchemy import Integer, String, Enum, JSON
from sqlalchemy.orm import Mapped, mapped_column

from .mission import Base
from .enums import AgentType, AvailabilityStatus


class Agent(Base):
    __tablename__ = "agents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    agent_type: Mapped[AgentType] = mapped_column(
        Enum(AgentType, name="agent_type_enum"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    capabilities: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    availability_status: Mapped[AvailabilityStatus] = mapped_column(
        Enum(AvailabilityStatus, name="availability_status_enum"),
        nullable=False,
        default=AvailabilityStatus.AVAILABLE,
    )
