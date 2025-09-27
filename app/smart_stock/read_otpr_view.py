#!/usr/bin/env python3
"""Read the 'otpr' view from Lakebase PostgreSQL database."""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from decimal import Decimal
from dotenv import load_dotenv

# Load environment variables
load_dotenv("../../.env.local")

# Database configuration
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

def check_views(conn):
    """List all views in the database."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT table_name
            FROM information_schema.views
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        views = cur.fetchall()
        return [v[0] for v in views]

def read_view_structure(conn, view_name):
    """Get the structure and definition of a view."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # Get column information
        cur.execute(f"""
            SELECT
                column_name,
                data_type,
                is_nullable
            FROM information_schema.columns
            WHERE table_name = '{view_name}'
            AND table_schema = 'public'
            ORDER BY ordinal_position
        """)
        columns = cur.fetchall()

        # Try to get view definition
        try:
            cur.execute(f"""
                SELECT pg_get_viewdef('{view_name}'::regclass, true) as definition
            """)
            view_def = cur.fetchone()
        except:
            view_def = None

        return columns, view_def

def read_view_data(conn, view_name, limit=20):
    """Read data from a view."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # Get count
        cur.execute(f"SELECT COUNT(*) as count FROM {view_name}")
        count = cur.fetchone()['count']

        # Get sample data
        cur.execute(f"SELECT * FROM {view_name} LIMIT {limit}")
        rows = cur.fetchall()

        return count, rows

def main():
    """Main function to read the OTPR view."""
    print("🔌 Connecting to Lakebase PostgreSQL Database...")
    print(f"   Host: {DB_CONFIG['host']}")
    print(f"   Database: {DB_CONFIG['database']}")
    print(f"   User: {DB_CONFIG['user']}")
    print()

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        print("✅ Successfully connected to database!\n")

        # List all views
        views = check_views(conn)
        print(f"📋 Found {len(views)} view(s) in the database:")
        for v in views:
            print(f"   • {v}")
        print()

        # Check if 'otpr' view exists
        if 'otpr' in views:
            print("="*80)
            print("📊 VIEW: otpr")
            print("="*80)

            # Get structure
            columns, view_def = read_view_structure(conn, 'otpr')

            print("\n📝 View Columns:")
            for col in columns:
                nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
                print(f"   • {col['column_name']}: {col['data_type']} ({nullable})")

            # Show view definition if available
            if view_def:
                print("\n🔍 View Definition:")
                print("-"*40)
                print(view_def['definition'])
                print("-"*40)

            # Get data
            try:
                count, rows = read_view_data(conn, 'otpr')

                print(f"\n📊 Total Rows: {count:,}")

                if rows:
                    print(f"\n📄 Sample Data (showing up to 20 rows):\n")

                    # Display each row
                    for i, row in enumerate(rows, 1):
                        print(f"Row {i}:")
                        formatted_row = {k: format_value(v) for k, v in row.items()}
                        for key, value in formatted_row.items():
                            print(f"  {key}: {value}")
                        print()

                        # Add separator between rows for readability
                        if i < len(rows):
                            print("-" * 40)
                else:
                    print("   (No data in this view)")

            except psycopg2.errors.InsufficientPrivilege:
                print("\n❌ No permission to read data from 'otpr' view")
            except Exception as e:
                print(f"\n❌ Error reading view data: {e}")

        else:
            print("❌ View 'otpr' not found in the database")

            # Check if it might be a table instead
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT tablename
                    FROM pg_tables
                    WHERE schemaname = 'public'
                    AND tablename = 'otpr'
                """)
                is_table = cur.fetchone()

                if is_table:
                    print("ℹ️  'otpr' exists as a TABLE, not a view. Reading table data...\n")

                    # Read as table
                    with conn.cursor(cursor_factory=RealDictCursor) as cur:
                        try:
                            cur.execute("SELECT COUNT(*) as count FROM otpr")
                            count = cur.fetchone()['count']
                            print(f"📊 Total Rows in table 'otpr': {count:,}")

                            cur.execute("SELECT * FROM otpr LIMIT 20")
                            rows = cur.fetchall()

                            if rows:
                                print(f"\n📄 Sample Data (first 20 rows):\n")
                                for i, row in enumerate(rows, 1):
                                    print(f"Row {i}:")
                                    formatted_row = {k: format_value(v) for k, v in row.items()}
                                    for key, value in formatted_row.items():
                                        print(f"  {key}: {value}")
                                    if i < len(rows):
                                        print("-" * 40)
                        except psycopg2.errors.InsufficientPrivilege:
                            print("❌ No permission to read table 'otpr'")
                        except psycopg2.errors.UndefinedTable:
                            print("❌ Neither view nor table 'otpr' exists in the database")

        conn.close()
        print("\n✅ Database connection closed.")

    except psycopg2.OperationalError as e:
        print(f"❌ Failed to connect to database: {e}")
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()