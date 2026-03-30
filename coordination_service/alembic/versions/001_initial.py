"""initial coordination tables

Revision ID: 001
Revises:
Create Date: 2026-03-30
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "missions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "incident_type",
            sa.Enum("BUILDING_COLLAPSE", "FIRE", "INDUSTRIAL_ACCIDENT", "FLOOD", "OTHER", name="incident_type_enum"),
            nullable=False,
        ),
        sa.Column("location", sa.String(255), nullable=False),
        sa.Column(
            "priority",
            sa.Enum("LOW", "MEDIUM", "HIGH", "CRITICAL", name="priority_enum"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("CREATED", "PLANNING", "IN_PROGRESS", "COMPLETED", "CANCELLED", name="mission_status_coord_enum"),
            nullable=False,
        ),
        sa.Column("required_agents", sa.Integer(), nullable=False, server_default="1"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "agents",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "agent_type",
            sa.Enum("GROUND_ROBOT", "UAV", name="agent_type_enum"),
            nullable=False,
        ),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("capabilities", sa.JSON(), nullable=True),
        sa.Column(
            "availability_status",
            sa.Enum("AVAILABLE", "BUSY", "OFFLINE", "MAINTENANCE", name="availability_status_enum"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "search_zones",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("mission_id", sa.Integer(), sa.ForeignKey("missions.id"), nullable=False),
        sa.Column("zone_code", sa.String(50), nullable=False),
        sa.Column("geometry", sa.JSON(), nullable=True),
        sa.Column(
            "priority",
            sa.Enum("LOW", "MEDIUM", "HIGH", "CRITICAL", name="priority_enum", create_type=False),
            nullable=False,
        ),
        sa.Column("assigned_agent_id", sa.Integer(), sa.ForeignKey("agents.id"), nullable=True),
        sa.Column(
            "status",
            sa.Enum("PENDING", "ASSIGNED", "IN_PROGRESS", "COMPLETED", "FAILED", name="zone_status_enum"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "routes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("mission_id", sa.Integer(), sa.ForeignKey("missions.id"), nullable=False),
        sa.Column("agent_id", sa.Integer(), sa.ForeignKey("agents.id"), nullable=False),
        sa.Column("zone_id", sa.Integer(), sa.ForeignKey("search_zones.id"), nullable=False),
        sa.Column("route_points", sa.JSON(), nullable=True),
        sa.Column("assigned_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column(
            "route_status",
            sa.Enum("PLANNED", "IN_PROGRESS", "COMPLETED", "CANCELLED", "REASSIGNED", name="route_status_enum"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "task_reassignments",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("mission_id", sa.Integer(), sa.ForeignKey("missions.id"), nullable=False),
        sa.Column("from_agent_id", sa.Integer(), sa.ForeignKey("agents.id"), nullable=False),
        sa.Column("to_agent_id", sa.Integer(), sa.ForeignKey("agents.id"), nullable=False),
        sa.Column("reason", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("task_reassignments")
    op.drop_table("routes")
    op.drop_table("search_zones")
    op.drop_table("agents")
    op.drop_table("missions")
    op.execute("DROP TYPE IF EXISTS incident_type_enum")
    op.execute("DROP TYPE IF EXISTS priority_enum")
    op.execute("DROP TYPE IF EXISTS mission_status_coord_enum")
    op.execute("DROP TYPE IF EXISTS agent_type_enum")
    op.execute("DROP TYPE IF EXISTS availability_status_enum")
    op.execute("DROP TYPE IF EXISTS zone_status_enum")
    op.execute("DROP TYPE IF EXISTS route_status_enum")
