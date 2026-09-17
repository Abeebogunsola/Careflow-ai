"""
SQLAlchemy Declarative Base Definition.

All database models will inherit from this Base class during the Database phase.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy declarative models.
    Provides metadata registry for Alembic migrations.
    """
    pass
