"""initial monitoring tables

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
        "telemetry_records",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("agent_id", sa.Integer(), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("battery_level", sa.Float(), nullable=False),
        sa.Column("speed", sa.Float(), nullable=False),
        sa.Column(
            "link_status",
            sa.Enum("ONLINE", "DEGRADED", "OFFLINE", name="link_status_enum"),
            nullable=False,
        ),
        sa.Column(
            "mission_status",
            sa.Enum("PENDING", "IN_PROGRESS", "COMPLETED", "ABORTED", name="mission_status_enum"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_telemetry_records_agent_id", "telemetry_records", ["agent_id"])

    op.create_table(
        "sensor_events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("agent_id", sa.Integer(), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column(
            "sensor_type",
            sa.Enum("CAMERA", "THERMAL", "GAS", name="sensor_type_enum"),
            nullable=False,
        ),
        sa.Column("value", sa.JSON(), nullable=True),
        sa.Column("event_type", sa.String(100), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_sensor_events_agent_id", "sensor_events", ["agent_id"])

    op.create_table(
        "alerts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("agent_id", sa.Integer(), nullable=False),
        sa.Column("mission_id", sa.Integer(), nullable=True),
        sa.Column(
            "alert_type",
            sa.Enum(
                "HUMAN_DETECTED", "OBSTACLE", "GAS_LEAK", "OVERHEAT",
                "LOW_BATTERY", "LINK_LOST", "MALFUNCTION", "FIRE",
                name="alert_type_enum",
            ),
            nullable=False,
        ),
        sa.Column(
            "severity",
            sa.Enum("LOW", "MEDIUM", "HIGH", "CRITICAL", name="alert_severity_enum"),
            nullable=False,
        ),
        sa.Column("message", sa.String(500), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("ACTIVE", "ACKNOWLEDGED", "RESOLVED", name="alert_status_enum"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_alerts_agent_id", "alerts", ["agent_id"])

    op.create_table(
        "agent_status",
        sa.Column("agent_id", sa.Integer(), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("battery_level", sa.Float(), nullable=False),
        sa.Column(
            "link_status",
            sa.Enum("ONLINE", "DEGRADED", "OFFLINE", name="link_status_enum", create_type=False),
            nullable=False,
        ),
        sa.Column(
            "health_state",
            sa.Enum("HEALTHY", "WARNING", "CRITICAL", "OFFLINE", name="health_state_enum"),
            nullable=False,
        ),
        sa.Column(
            "mission_status",
            sa.Enum("PENDING", "IN_PROGRESS", "COMPLETED", "ABORTED", name="mission_status_enum", create_type=False),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("agent_id"),
    )


def downgrade() -> None:
    op.drop_table("agent_status")
    op.drop_table("alerts")
    op.drop_table("sensor_events")
    op.drop_table("telemetry_records")
    op.execute("DROP TYPE IF EXISTS link_status_enum")
    op.execute("DROP TYPE IF EXISTS mission_status_enum")
    op.execute("DROP TYPE IF EXISTS sensor_type_enum")
    op.execute("DROP TYPE IF EXISTS alert_type_enum")
    op.execute("DROP TYPE IF EXISTS alert_severity_enum")
    op.execute("DROP TYPE IF EXISTS alert_status_enum")
    op.execute("DROP TYPE IF EXISTS health_state_enum")
