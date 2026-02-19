"""
Database engine and session factory.
Uses settings for DATABASE_URL (SQLite for dev/test, PostgreSQL for production).
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from .settings import Settings
from ..adapters.output.persistence.models import Base


def get_engine(database_url: str | None = None):
    """Create SQLAlchemy engine. Use in-memory SQLite when database_url is not set (tests)."""
    url = database_url or "sqlite:///:memory:"
    connect_args = {} if "sqlite" not in url else {"check_same_thread": False}
    return create_engine(url, connect_args=connect_args, echo=False)


def get_session_factory(settings: Settings | None = None):
    """Return a session factory bound to the configured engine."""
    s = settings or Settings()
    engine = get_engine(s.database_url)
    Base.metadata.create_all(engine)
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_session(settings: Settings | None = None) -> Session:
    """Return a new session (for use with Depends)."""
    factory = get_session_factory(settings)
    return factory()
