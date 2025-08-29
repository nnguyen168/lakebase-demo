#!/usr/bin/env python3
"""Initialize Lakebase PostgreSQL database with tables and sample data."""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables from .env.local
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / '.env.local'
load_dotenv(env_path)

from server.postgres_database import db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Initialize Lakebase database with tables and sample data."""
    try:
        logger.info("Starting Lakebase PostgreSQL database initialization...")
        
        # Create tables
        logger.info("Creating database tables...")
        db.create_tables()
        logger.info("Database tables created successfully!")
        
        # Seed sample data
        logger.info("Seeding sample data...")
        db.seed_sample_data()
        logger.info("Sample data seeded successfully!")
        
        # Verify the setup
        logger.info("Verifying database setup...")
        
        # Check table counts
        tables = ['customers', 'products', 'orders', 'inventory_forecast']
        for table in tables:
            result = db.execute_query(f"SELECT COUNT(*) as count FROM {table}")
            count = result[0]['count'] if result else 0
            logger.info(f"  {table}: {count} records")
        
        logger.info("Lakebase database initialization completed successfully!")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        sys.exit(1)
    finally:
        # Close the connection pool
        db.close()


if __name__ == "__main__":
    main()