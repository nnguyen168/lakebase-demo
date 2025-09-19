"""Database selector - only uses real PostgreSQL database."""

import os

# Check if we have real database credentials
use_real_db = all([
    os.getenv("DB_HOST"),
    os.getenv("DB_USER"),
    os.getenv("DB_PASSWORD")
])

if not use_real_db:
    raise ValueError("PostgreSQL database credentials are required. Please set DB_HOST, DB_USER, and DB_PASSWORD environment variables.")

# Only use real PostgreSQL database - no fallback
from .postgres_database import db
print("Using Lakebase PostgreSQL database")

__all__ = ['db']