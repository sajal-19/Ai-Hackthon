# app/core/db_init.py

from app.db.session import engine
from app.db.base import Base


def create_tables() -> None:
    """
    Create all database tables defined on the SQLAlchemy Base metadata.
    Safe to call on application startup for an MVP.
    Existing tables are left unchanged.
    """
    Base.metadata.create_all(bind=engine)
