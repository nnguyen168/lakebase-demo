#!/usr/bin/env python3
"""Read data from Lakebase PostgreSQL database - simplified version."""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from decimal import Decimal
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv(".env.local")

# Database configuration from environment
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "instance-9965ce63-150c-4746-93dc-a3dcb78fda3b.database.cloud.databricks.com"),
    "port": os.getenv("DB_PORT", "5432"),
    "database": os.getenv("DB_NAME", "databricks_postgres"),
    "user": os.getenv("DB_USER", "lakebase_demo_app"),
    "password": os.getenv("DB_PASSWORD", "lakebasedemo2025"),
}

def format_value(value):
    """Format values for display."""
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    elif isinstance(value, Decimal):
        return float(value)
    elif value is None:
        return None
    return value

def main():
    """Main function to read and display database data."""
    print("🔌 Connecting to Lakebase PostgreSQL Database...")
    print(f"   Host: {DB_CONFIG['host']}")
    print(f"   Database: {DB_CONFIG['database']}")
    print(f"   User: {DB_CONFIG['user']}")
    print()

    # List of specific tables we want to read
    tables_to_check = [
        'products',
        'warehouses',
        'inventory_forecast',
        'inventory_transactions',
        'inventory_historical',
        'fact_inventory_transactions'
    ]

    for table_name in tables_to_check:
        try:
            # Create a new connection for each table to avoid transaction issues
            conn = psycopg2.connect(**DB_CONFIG)
            conn.autocommit = True  # Set autocommit to avoid transaction blocks

            print(f"\n{'='*60}")
            print(f"📋 Checking table: {table_name}")
            print(f"{'='*60}")

            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Try to get count
                try:
                    cur.execute(f"SELECT COUNT(*) as count FROM {table_name}")
                    count = cur.fetchone()['count']
                    print(f"✅ Row count: {count}")
                except psycopg2.errors.InsufficientPrivilege:
                    print(f"❌ No permission to access table '{table_name}'")
                    conn.close()
                    continue
                except psycopg2.errors.UndefinedTable:
                    print(f"❌ Table '{table_name}' does not exist")
                    conn.close()
                    continue

                # If we can access the table, get sample data
                if count > 0:
                    cur.execute(f"SELECT * FROM {table_name} LIMIT 5")
                    rows = cur.fetchall()

                    print(f"\n📄 Sample data (first 5 rows):")
                    for i, row in enumerate(rows, 1):
                        print(f"\n  Row {i}:")
                        formatted_row = {k: format_value(v) for k, v in row.items()}
                        for key, value in formatted_row.items():
                            print(f"    {key}: {value}")
                else:
                    print("   (No data in this table)")

            conn.close()

        except psycopg2.OperationalError as e:
            print(f"❌ Connection error: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")

    print("\n" + "="*60)
    print("✅ Database exploration complete!")

if __name__ == "__main__":
    main()