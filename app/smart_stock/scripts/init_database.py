#!/usr/bin/env python3
"""Initialize Lakebase database with tables and sample data."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.db_selector import db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Initialize database with tables and sample data."""
    try:
        logger.info("Starting database initialization...")
        
        # Create tables
        logger.info("Creating database tables...")
        db.create_tables()
        logger.info("Database tables created successfully!")
        
        # Seed sample data
        logger.info("Seeding sample data...")
        db.seed_sample_data()
        logger.info("Sample data seeded successfully!")
        
        logger.info("Database initialization completed successfully!")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()