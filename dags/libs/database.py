"""
Database Operations Module

This module provides functions to connect to PostgreSQL and perform basic database operations
using SQLAlchemy and pandas.
"""

import os
from pathlib import Path
from typing import Optional

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

# Load environment variables from the .env file in the project root
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path)


def create_postgres_engine(database: str = None) -> Engine:
    """
    Create a SQLAlchemy engine for a PostgreSQL database using credentials from a .env file.

    Args:
        database: Database name (defaults to POSTGRES_DB from .env)

    Returns:
        Engine: SQLAlchemy Engine instance.

    Raises:
        SQLAlchemyError: If connection to database fails
    """
    try:
        user = os.getenv("POSTGRES_USER")
        password = os.getenv("POSTGRES_PASSWORD")
        host = os.getenv("POSTGRES_HOST")
        port = os.getenv("POSTGRES_PORT", "5432")
        database = database or os.getenv("POSTGRES_DB")

        if None in (user, password, host, port, database):
            raise ValueError("Missing required database credentials in environment variables")

        url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
        engine = create_engine(url)

        return engine
    except SQLAlchemyError as e:
        print(f"Error connecting to database: {e}")
        raise
    except ValueError as e:
        print(f"Configuration error: {e}")
        raise


def create_database(db_name: str = None) -> bool:
    """
    Create a new PostgreSQL database using POSTGRES_DB from .env as default.

    Args:
        db_name: Name of database to create (defaults to POSTGRES_DB from .env)

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Use provided name or fall back to environment variable
        db_to_create = db_name or os.getenv("POSTGRES_DB")

        # Connect to default database (POSTGRES_DB_DEFAULT or 'postgres')
        engine = create_postgres_engine(database="postgres")

        with engine.connect() as conn:
            # Set to autocommit for DB creation
            conn.execution_options(isolation_level="AUTOCOMMIT")

            # Create new database
            conn.execute(text(f"CREATE DATABASE {db_to_create}"))

        print(f"Successfully created database '{db_to_create}'")
        return True
    except SQLAlchemyError as e:
        print(f"Error creating database: {e}")
        return False

    except Exception as e:
        print(f"Unexpected error: {e}")
        return False


def write_dataframe_to_table(
    df: pd.DataFrame,
    table_name: str,
    engine: Engine,
    schema: str = "public",
    if_exists: str = "append",
    index: bool = False,
) -> bool:
    """
    Write a pandas DataFrame to a PostgreSQL table.

    Args:
        df: DataFrame to write to database
        table_name: Name of the target table
        engine: SQLAlchemy Engine instance
        schema: Database schema name (default: 'public')
        if_exists: How to behave if table exists {'fail', 'replace', 'append'}
        index: Write DataFrame index as a column

    Returns:
        bool: True if operation succeeded, False otherwise
    """
    try:
        with engine.begin() as connection:
            df.to_sql(
                name=table_name, con=connection, schema=schema, if_exists=if_exists, index=index
            )
        print(f"Successfully wrote data to table {schema}.{table_name}")
        return True
    except SQLAlchemyError as e:
        print(f"Error writing to table {schema}.{table_name}: {e}")
        return False


def read_from_table(
    table_name: str, engine: Engine, schema: str = "public", query: str = None
) -> Optional[pd.DataFrame]:
    """
    Read data from a PostgreSQL table into a pandas DataFrame.

    Args:
        table_name: Name of the table to read from
        engine: SQLAlchemy Engine instance
        schema: Database schema name (default: 'public')
        query: Optional SQL query to filter data (uses SELECT * if None)

    Returns:
        Optional[pd.DataFrame]: DataFrame containing the query results or None if error occurs
    """
    try:
        with engine.connect() as connection:
            if query is None:
                query = f"SELECT * FROM {schema}.{table_name}"

            df = pd.read_sql(text(query), connection)
            print(f"Successfully read data from table {schema}.{table_name}")
            return df
    except SQLAlchemyError as e:
        print(f"Error reading from table {schema}.{table_name}: {e}")
        return None
