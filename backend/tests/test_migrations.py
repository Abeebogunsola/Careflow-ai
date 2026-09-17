"""
Migration Tests for CareFlow AI.

Verifies Alembic discovery, schema generation, upgrade, downgrade, and static SQL generation.
"""

from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic import command
from sqlalchemy import create_engine, inspect


def test_alembic_discovers_initial_migration():
    """Verify that Alembic detects 0001_initial_schema as the head revision."""
    cfg = Config("alembic.ini")
    script = ScriptDirectory.from_config(cfg)
    heads = script.get_revisions("heads")
    assert len(heads) == 1
    assert heads[0].revision == "0001_initial_schema"


def test_alembic_upgrade_creates_all_tables():
    """Verify applying the initial migration creates all 10 tables plus alembic_version."""
    engine = create_engine("sqlite:///:memory:")
    cfg = Config("alembic.ini")

    with engine.connect() as conn:
        cfg.attributes["connection"] = conn
        command.upgrade(cfg, "head")

        inspector = inspect(conn)
        tables = set(inspector.get_table_names())

        expected = {
            "alembic_version",
            "roles",
            "users",
            "clients",
            "communication_preferences",
            "appointments",
            "interactions",
            "follow_up_tasks",
            "escalations",
            "approved_information",
            "audit_logs",
        }
        assert expected.issubset(tables)


def test_alembic_downgrade_rolls_back_cleanly():
    """Verify that downgrading to base drops all application tables."""
    engine = create_engine("sqlite:///:memory:")
    cfg = Config("alembic.ini")

    with engine.connect() as conn:
        cfg.attributes["connection"] = conn
        command.upgrade(cfg, "head")
        command.downgrade(cfg, "base")

        inspector = inspect(conn)
        tables = set(inspector.get_table_names())
        # All application tables dropped; only alembic_version remains
        assert "roles" not in tables
        assert "users" not in tables
        assert "clients" not in tables
        assert "appointments" not in tables


def test_offline_sql_generation_contains_postgresql_types():
    """Verify offline SQL generation produces PostgreSQL DDL with UUID and TIMESTAMPTZ."""
    from io import StringIO
    import sys

    cfg = Config("alembic.ini")
    old_stdout = sys.stdout
    sys.stdout = buffer = StringIO()

    try:
        command.upgrade(cfg, "0001_initial_schema", sql=True)
    finally:
        sys.stdout = old_stdout

    sql = buffer.getvalue()
    assert "CREATE TABLE roles" in sql
    assert "CREATE TABLE clients" in sql
    assert "CREATE TABLE appointments" in sql
    assert "TIMESTAMP WITH TIME ZONE" in sql
    assert "UUID" in sql
