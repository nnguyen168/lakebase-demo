"""Database selector - chooses between mock and real database based on environment."""

import os

# Check if we have real database credentials
use_real_db = all([
    os.getenv("DB_HOST"),
    os.getenv("DB_USER"),
    os.getenv("DB_PASSWORD")
])

if use_real_db:
    try:
        from .postgres_database import db
        print("Using Lakebase PostgreSQL database")
    except Exception as e:
        print(f"Failed to connect to PostgreSQL, falling back to mock: {e}")
        from .mock_database import db
else:
    from .mock_database import db
    print("Using mock database (no DB credentials found)")

__all__ = ['db']