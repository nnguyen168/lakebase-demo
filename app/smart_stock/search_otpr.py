#!/usr/bin/env python3
"""Search for 'otpr' object in all schemas of the database."""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
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

def search_for_otpr(conn):
    """Search for 'otpr' in all schemas."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        print("🔍 Searching for 'otpr' in the database...\n")

        # Search in all tables
        print("📋 Searching in TABLES:")
        cur.execute("""
            SELECT
                schemaname as schema,
                tablename as name,
                tableowner as owner
            FROM pg_tables
            WHERE tablename ILIKE '%otpr%'
            ORDER BY schemaname, tablename
        """)
        tables = cur.fetchall()

        if tables:
            for t in tables:
                print(f"   ✅ Found table: {t['schema']}.{t['name']} (owner: {t['owner']})")
        else:
            print("   ❌ No tables found with 'otpr' in the name")

        # Search in all views
        print("\n📋 Searching in VIEWS:")
        cur.execute("""
            SELECT
                schemaname as schema,
                viewname as name,
                viewowner as owner
            FROM pg_views
            WHERE viewname ILIKE '%otpr%'
            ORDER BY schemaname, viewname
        """)
        views = cur.fetchall()

        if views:
            for v in views:
                print(f"   ✅ Found view: {v['schema']}.{v['name']} (owner: {v['owner']})")
        else:
            print("   ❌ No views found with 'otpr' in the name")

        # Search in all schemas
        print("\n📋 Available SCHEMAS:")
        cur.execute("""
            SELECT nspname as schema_name
            FROM pg_namespace
            WHERE nspname NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
            ORDER BY nspname
        """)
        schemas = cur.fetchall()

        for s in schemas:
            print(f"   • {s['schema_name']}")

        # List all accessible tables (not just those with 'otpr')
        print("\n📋 All accessible TABLES in 'public' schema:")
        cur.execute("""
            SELECT tablename
            FROM pg_tables
            WHERE schemaname = 'public'
            ORDER BY tablename
        """)
        all_tables = cur.fetchall()

        for t in all_tables:
            print(f"   • {t['tablename']}")

        # List all accessible views
        print("\n📋 All accessible VIEWS in 'public' schema:")
        cur.execute("""
            SELECT viewname
            FROM pg_views
            WHERE schemaname = 'public'
            ORDER BY viewname
        """)
        all_views = cur.fetchall()

        if all_views:
            for v in all_views:
                print(f"   • {v['viewname']}")
        else:
            print("   (No views found)")

        # Check if there's a different case variation
        print("\n🔍 Checking case variations of 'otpr':")
        variations = ['otpr', 'OTPR', 'Otpr', 'OtPr']
        for var in variations:
            cur.execute(f"""
                SELECT EXISTS (
                    SELECT 1 FROM pg_tables WHERE tablename = '{var}'
                    UNION
                    SELECT 1 FROM pg_views WHERE viewname = '{var}'
                ) as exists
            """)
            exists = cur.fetchone()['exists']
            if exists:
                print(f"   ✅ Found exact match: '{var}'")
            else:
                print(f"   ❌ No exact match for: '{var}'")

def main():
    """Main function."""
    print("🔌 Connecting to Lakebase PostgreSQL Database...")
    print(f"   Host: {DB_CONFIG['host']}")
    print(f"   Database: {DB_CONFIG['database']}")
    print(f"   User: {DB_CONFIG['user']}")
    print()

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        print("✅ Successfully connected to database!\n")

        search_for_otpr(conn)

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