"""
Database configuration and session management for the Proof-of-Work Hiring Platform.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from contextlib import contextmanager
from typing import Generator

# Database URL from environment variable
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/hiring_platform"
)

# Create engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using
    echo=os.getenv("SQL_ECHO", "false").lower() == "true",  # SQL logging
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency for database sessions.

    Yields:
        Database session that auto-closes after request

    Example:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    """
    Context manager for database sessions (for non-FastAPI code).

    Example:
        with get_db_context() as db:
            user = db.query(User).first()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_database():
    """
    Initialize the database (create all tables).
    Run this once during initial setup.
    """
    from models import Base
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized successfully!")


def reset_database():
    """
    ⚠️  WARNING: Drops and recreates all tables!
    Only use in development.
    """
    from models import Base
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("⚠️  Database reset complete!")


if __name__ == "__main__":
    print(f"Database URL: {DATABASE_URL}")
    print("Run init_database() to create tables")
