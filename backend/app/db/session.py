"""
SQLAlchemy Session and Database Engine Configuration.

Establishes connection pooling and session management for PostgreSQL.
Lazy evaluation ensures that basic application startup and health probes
do not fail if PostgreSQL is not yet initialized.
"""

from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings

# Create database engine with connection pooling and pre-ping
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_pre_ping=True,
    echo=settings.DB_ECHO,
)

# Session factory for local request scopes
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a SQLAlchemy database session
    and guarantees proper session cleanup after request completion.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
