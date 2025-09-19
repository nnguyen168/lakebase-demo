#!/usr/bin/env python3
"""Initialize Lakebase PostgreSQL database with tables and sample data."""

import sys
import os
from pathlib import Path

# Load environment variables first
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env.local'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"Loaded environment from {env_path}")
except ImportError:
    print("dotenv not available")

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Initialize PostgreSQL database with tables and sample data."""
    try:
        # Import after env vars are loaded
        from server.postgres_database import LakebasePostgresConnection
        
        logger.info("Starting PostgreSQL database initialization...")
        
        # Create database connection
        db = LakebasePostgresConnection()
        logger.info("PostgreSQL connection established")
        
        # Create tables
        logger.info("Creating database tables...")
        db.create_tables()
        logger.info("Database tables created successfully!")
        
        # Seed sample data
        logger.info("Seeding sample data...")
        db.seed_sample_data()
        logger.info("Sample data seeded successfully!")
        
        logger.info("PostgreSQL database initialization completed successfully!")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()