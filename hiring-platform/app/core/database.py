"""
Database configuration and session management.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator

from app.core.config import settings

# Create engine with settings
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using
    echo=settings.SQL_ECHO,  # SQL logging from config
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
    from app.models import Base
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized successfully!")


def reset_database():
    """
    ⚠️  WARNING: Drops and recreates all tables!
    Only use in development.
    """
    from app.models import Base
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("⚠️  Database reset complete!")
