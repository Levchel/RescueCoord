from sqlalchemy import Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .mission import Base


class TaskReassignment(Base):
    __tablename__ = "task_reassignments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    mission_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("missions.id"), nullable=False
    )
    from_agent_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("agents.id"), nullable=False
    )
    to_agent_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("agents.id"), nullable=False
    )
    reason: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    from_agent = relationship("Agent", foreign_keys=[from_agent_id], lazy="selectin")
    to_agent = relationship("Agent", foreign_keys=[to_agent_id], lazy="selectin")
