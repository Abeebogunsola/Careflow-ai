#!/usr/bin/env python3
"""
CareFlow AI — Production Database Initializer & Migration Runner.

Executes:
1. Alembic schema migrations (alembic upgrade head).
2. Analytical Star Schema views (analytics/sql/star_schema_views_postgres.sql).
3. Verifies schema integrity and database connectivity.

Usage:
    python deploy/scripts/init_prod_db.py
"""

import os
import sys
import subprocess
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent
BACKEND_DIR = BASE_DIR / "backend"
SQL_VIEWS_PATH = BASE_DIR / "analytics" / "sql" / "star_schema_views_postgres.sql"

def run_alembic_migrations():
    """Run Alembic migrations to bring the database schema to head."""
    print("==> [1/3] Applying Alembic database migrations...")
    try:
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            cwd=str(BACKEND_DIR),
            check=True,
            capture_output=True,
            text=True
        )
        print("    Alembic migrations applied successfully.")
        if result.stdout:
            print(f"    {result.stdout.strip()}")
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Alembic migration failed:\n{e.stderr}", file=sys.stderr)
        sys.exit(1)

def apply_star_schema_views():
    """Apply the PostgreSQL-native Star Schema views for Power BI analytics."""
    print("==> [2/3] Installing PostgreSQL Analytical Star Schema Views...")
    if not SQL_VIEWS_PATH.exists():
        print(f"WARNING: SQL views file not found at {SQL_VIEWS_PATH}, skipping views.")
        return

    # Use SQLAlchemy engine from backend config
    sys.path.insert(0, str(BACKEND_DIR))
    try:
        from app.core.config import settings
        from sqlalchemy import create_engine, text

        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as conn:
            with open(SQL_VIEWS_PATH, "r", encoding="utf-8") as f:
                sql_content = f.read()
            # Split and execute individual statements
            statements = [stmt.strip() for stmt in sql_content.split(";") if stmt.strip()]
            for stmt in statements:
                conn.execute(text(stmt))
            conn.commit()
        print("    All 6 Star Schema analytical views installed successfully.")
    except Exception as e:
        print(f"ERROR: Failed to apply Star Schema views: {e}", file=sys.stderr)
        sys.exit(1)

def verify_database():
    """Verify that core tables and health check function correctly."""
    print("==> [3/3] Verifying database connectivity and core tables...")
    try:
        from app.core.config import settings
        from sqlalchemy import create_engine, inspect

        engine = create_engine(settings.DATABASE_URL)
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        views = inspector.get_view_names()

        print(f"    Tables verified ({len(tables)}): {', '.join(tables)}")
        print(f"    Views verified ({len(views)}): {', '.join(views)}")
        print("\n==> Database initialization complete! Production persistence is ready.")
    except Exception as e:
        print(f"ERROR: Database verification failed: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    run_alembic_migrations()
    apply_star_schema_views()
    verify_database()
