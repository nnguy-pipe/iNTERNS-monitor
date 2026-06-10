"""SQLite database initialization and configuration."""

import os
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import declarative_base, Session, sessionmaker

# Base model for all ORM models
Base = declarative_base()

# Database connection settings
DATABASE_DIR = os.getenv("DATABASE_DIR", ".")
DATABASE_PATH = os.path.join(DATABASE_DIR, "ahms.db")
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Create engine with SQLite
engine: Engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=os.getenv("SQL_ECHO", "false").lower() == "true",
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Session:
    """Dependency injection for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create all tables in the database."""
    Base.metadata.create_all(bind=engine)


def drop_db() -> None:
    """Drop all tables from the database (for testing only)."""
    Base.metadata.drop_all(bind=engine)
