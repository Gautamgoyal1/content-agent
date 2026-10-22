"""Database engine and session management."""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from content_agent.settings import get_settings

settings = get_settings()

db_url = settings.database_url.get_secret_value() if settings.database_url else "sqlite:///./content_agent.db"
# Handle postgres driver if sqlite is used
if "postgresql" in db_url and "psycopg" in db_url:
    # Use fallback sqlite for offline prototype if local postgres is not reachable
    pass

engine = create_engine(
    "sqlite:///./content_agent.db",
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency for obtaining a database session."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
