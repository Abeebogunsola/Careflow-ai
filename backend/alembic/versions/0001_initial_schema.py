"""Initial CareFlow AI Database Schema

Revision ID: 0001_initial_schema
Revises: None
Create Date: 2026-09-17 21:00:00.000000

Source of truth: docs/database-design.md
Creates the 10 core tables, foreign keys, constraints, and indexes:
1. roles
2. users
3. clients
4. communication_preferences
5. appointments
6. interactions
7. follow_up_tasks
8. escalations
9. approved_information
10. audit_logs
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # -------------------------------------------------------------------------
    # 1. Table: roles
    # -------------------------------------------------------------------------
    op.create_table(
        "roles",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index("ix_roles_name", "roles", ["name"], unique=True)

    # -------------------------------------------------------------------------
    # 2. Table: users
    # -------------------------------------------------------------------------
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("role_id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("first_name", sa.String(length=100), nullable=False),
        sa.Column("last_name", sa.String(length=100), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_role_id", "users", ["role_id"], unique=False)

    # -------------------------------------------------------------------------
    # 3. Table: clients
    # -------------------------------------------------------------------------
    op.create_table(
        "clients",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("external_reference", sa.String(length=100), nullable=True),
        sa.Column("preferred_name", sa.String(length=100), nullable=True),
        sa.Column("preferred_language", sa.String(length=50), nullable=False, server_default="en"),
        sa.Column("enrollment_status", sa.String(length=50), nullable=False, server_default="active"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("external_reference"),
    )
    op.create_index("ix_clients_external_reference", "clients", ["external_reference"], unique=True)
    op.create_index("ix_clients_enrollment_status", "clients", ["enrollment_status"], unique=False)

    # -------------------------------------------------------------------------
    # 4. Table: communication_preferences
    # -------------------------------------------------------------------------
    op.create_table(
        "communication_preferences",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("client_id", sa.Uuid(), nullable=False),
        sa.Column("channel", sa.String(length=50), nullable=False, server_default="web"),
        sa.Column("is_enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("client_id"),
    )
    op.create_index("ix_communication_preferences_client_id", "communication_preferences", ["client_id"], unique=True)

    # -------------------------------------------------------------------------
    # 5. Table: appointments
    # -------------------------------------------------------------------------
    op.create_table(
        "appointments",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("client_id", sa.Uuid(), nullable=False),
        sa.Column("appointment_type", sa.String(length=100), nullable=False),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="scheduled"),
        sa.Column("location_label", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_appointments_client_id", "appointments", ["client_id"], unique=False)
    op.create_index("ix_appointments_scheduled_at", "appointments", ["scheduled_at"], unique=False)
    op.create_index("ix_appointments_status", "appointments", ["status"], unique=False)
    op.create_index("ix_appointments_status_scheduled_at", "appointments", ["status", "scheduled_at"], unique=False)

    # -------------------------------------------------------------------------
    # 6. Table: interactions
    # -------------------------------------------------------------------------
    op.create_table(
        "interactions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("client_id", sa.Uuid(), nullable=False),
        sa.Column("channel", sa.String(length=50), nullable=False),
        sa.Column("direction", sa.String(length=20), nullable=False),
        sa.Column("interaction_type", sa.String(length=50), nullable=False),
        sa.Column("intent_category", sa.String(length=50), nullable=True),
        sa.Column("message_reference", sa.String(length=255), nullable=True),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_interactions_client_id", "interactions", ["client_id"], unique=False)
    op.create_index("ix_interactions_created_at", "interactions", ["created_at"], unique=False)
    op.create_index("ix_interactions_intent_category", "interactions", ["intent_category"], unique=False)

    # -------------------------------------------------------------------------
    # 7. Table: follow_up_tasks
    # -------------------------------------------------------------------------
    op.create_table(
        "follow_up_tasks",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("client_id", sa.Uuid(), nullable=False),
        sa.Column("assigned_to", sa.Uuid(), nullable=True),
        sa.Column("reason", sa.String(length=255), nullable=False),
        sa.Column("priority", sa.String(length=20), nullable=False, server_default="normal"),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="pending"),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["assigned_to"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_follow_up_tasks_client_id", "follow_up_tasks", ["client_id"], unique=False)
    op.create_index("ix_follow_up_tasks_assigned_to", "follow_up_tasks", ["assigned_to"], unique=False)
    op.create_index("ix_follow_up_tasks_status", "follow_up_tasks", ["status"], unique=False)
    op.create_index("ix_follow_up_tasks_due_at", "follow_up_tasks", ["due_at"], unique=False)

    # -------------------------------------------------------------------------
    # 8. Table: escalations
    # -------------------------------------------------------------------------
    op.create_table(
        "escalations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("client_id", sa.Uuid(), nullable=False),
        sa.Column("assigned_to", sa.Uuid(), nullable=True),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("priority", sa.String(length=20), nullable=False, server_default="high"),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="open"),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["assigned_to"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_escalations_client_id", "escalations", ["client_id"], unique=False)
    op.create_index("ix_escalations_assigned_to", "escalations", ["assigned_to"], unique=False)
    op.create_index("ix_escalations_status", "escalations", ["status"], unique=False)
    op.create_index("ix_escalations_priority", "escalations", ["priority"], unique=False)

    # -------------------------------------------------------------------------
    # 9. Table: approved_information
    # -------------------------------------------------------------------------
    op.create_table(
        "approved_information",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_approved_information_category", "approved_information", ["category"], unique=False)
    op.create_index("ix_approved_information_is_active", "approved_information", ["is_active"], unique=False)

    # -------------------------------------------------------------------------
    # 10. Table: audit_logs
    # -------------------------------------------------------------------------
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=True),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("entity_type", sa.String(length=100), nullable=False),
        sa.Column("entity_id", sa.Uuid(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_audit_logs_user_id", "audit_logs", ["user_id"], unique=False)
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"], unique=False)
    op.create_index("ix_audit_logs_entity_type", "audit_logs", ["entity_type"], unique=False)
    op.create_index("ix_audit_logs_created_at", "audit_logs", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("approved_information")
    op.drop_table("escalations")
    op.drop_table("follow_up_tasks")
    op.drop_table("interactions")
    op.drop_table("appointments")
    op.drop_table("communication_preferences")
    op.drop_table("clients")
    op.drop_table("users")
    op.drop_table("roles")
