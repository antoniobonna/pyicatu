"""
Configuration settings for the FastAPI application.
"""

import os

from dotenv import load_dotenv
from pydantic import PostgresDsn

# Load environment variables from .env file
load_dotenv()

# Database settings
POSTGRES_SERVER = os.getenv("POSTGRES_HOST")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

# Build database URI
SQLALCHEMY_DATABASE_URI = PostgresDsn.build(
    scheme="postgresql+psycopg2",
    username=POSTGRES_USER,
    password=POSTGRES_PASSWORD,
    host=POSTGRES_SERVER,
    port=int(POSTGRES_PORT),
    path=f"{POSTGRES_DB}",
)
