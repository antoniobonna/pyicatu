"""
Database connection utilities using SQLAlchemy.
"""

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from pyicatu.settings.config import DatabaseConfig


def create_postgres_engine() -> Engine:
    """
    Create a SQLAlchemy engine for PostgreSQL with connection pooling.

    Args:
        database: Optional database name override

    Returns:
        Engine: SQLAlchemy engine instance

    Raises:
        SQLAlchemyError: If connection fails
        ValueError: If missing required configs
    """
    if not DatabaseConfig.validate():
        raise ValueError("Missing required database credentials in environment variables")

    try:
        conn_params = DatabaseConfig.get_connection_dict()
        url = f"postgresql+psycopg2://{conn_params['user']}:{conn_params['password']}@{conn_params['host']}:{conn_params['port']}/{conn_params['database']}"

        return create_engine(url)
    except SQLAlchemyError as e:
        raise SQLAlchemyError(f"Database connection failed: {e}") from e
