"""
Database configuration settings loaded from environment variables.
"""

import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class DatabaseConfig:
    """
    PostgreSQL database configuration from environment variables.
    """

    USER = os.getenv("POSTGRES_USER")
    PASSWORD = os.getenv("POSTGRES_PASSWORD")
    HOST = os.getenv("POSTGRES_HOST")
    PORT = os.getenv("POSTGRES_PORT", "5432")
    DB = os.getenv("POSTGRES_DB")

    @classmethod
    def validate(cls) -> bool:
        """Check if all required configs are present."""
        return all([cls.USER, cls.PASSWORD, cls.HOST, cls.PORT, cls.DB])

    @classmethod
    def get_connection_dict(cls) -> dict:
        """Returns connection parameters as a dictionary."""
        return {
            "user": cls.USER,
            "password": cls.PASSWORD,
            "host": cls.HOST,
            "port": cls.PORT,
            "database": cls.DB,
        }
