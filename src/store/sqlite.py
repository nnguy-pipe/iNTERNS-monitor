"""SQLite database initialization and configuration."""

import os
from sqlalchemy import create_engine, Engine, event
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
    connect_args={
        "check_same_thread": False,
        "timeout": 30.0,  # 30 second timeout for lock waits
    },
    echo=os.getenv("SQL_ECHO", "false").lower() == "true",
    pool_pre_ping=True,  # Verify connections before using
)

# Set SQLite pragmas for reliability
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Configure SQLite pragmas for better concurrency and reliability."""
    cursor = dbapi_connection.cursor()
    # Enable WAL mode for concurrent reads
    cursor.execute("PRAGMA journal_mode=WAL")
    # Increase cache size for better performance
    cursor.execute("PRAGMA cache_size=5000")
    # Set synchronous mode to NORMAL for better performance with WAL
    cursor.execute("PRAGMA synchronous=NORMAL")
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

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
