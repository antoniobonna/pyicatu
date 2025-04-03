"""
Database session configuration.
"""

from core.config import SQLALCHEMY_DATABASE_URI
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Create database engine
engine = create_engine(str(SQLALCHEMY_DATABASE_URI))

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for SQLAlchemy models
Base = declarative_base()


def get_db():
    """
    Dependency function to get a database session.

    Yields:
        SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
