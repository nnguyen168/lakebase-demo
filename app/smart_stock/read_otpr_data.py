#!/usr/bin/env python3
"""Read data from the 'otpr' view in Lakebase PostgreSQL."""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from decimal import Decimal
from dotenv import load_dotenv
from tabulate import tabulate

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
        return f"{float(value):.2f}"
    elif value is None:
        return "NULL"
    return str(value)

def main():
    """Read and display data from the otpr view."""
    print("🔌 Connecting to Lakebase PostgreSQL Database...")
    print(f"   Host: {DB_CONFIG['host'][:50]}...")
    print(f"   Database: {DB_CONFIG['database']}")
    print(f"   User: {DB_CONFIG['user']}")
    print()

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        print("✅ Successfully connected to database!\n")

        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Get view structure
            print("="*80)
            print("📊 VIEW: public.otpr")
            print("="*80)

            # Get column information
            cur.execute("""
                SELECT
                    column_name,
                    data_type,
                    is_nullable
                FROM information_schema.columns
                WHERE table_name = 'otpr'
                AND table_schema = 'public'
                ORDER BY ordinal_position
            """)
            columns = cur.fetchall()

            print("\n📝 View Structure:")
            col_data = [[col['column_name'], col['data_type'],
                        'YES' if col['is_nullable'] == 'YES' else 'NO']
                       for col in columns]
            print(tabulate(col_data, headers=['Column', 'Type', 'Nullable'], tablefmt='grid'))

            # Try to get view definition
            try:
                cur.execute("SELECT pg_get_viewdef('public.otpr'::regclass, true) as definition")
                view_def = cur.fetchone()
                if view_def:
                    print("\n🔍 View Definition:")
                    print("-"*60)
                    print(view_def['definition'])
                    print("-"*60)
            except:
                pass

            # Get row count
            try:
                cur.execute("SELECT COUNT(*) as count FROM public.otpr")
                count = cur.fetchone()['count']
                print(f"\n📊 Total Rows: {count:,}")

                # Get sample data
                cur.execute("SELECT * FROM public.otpr LIMIT 25")
                rows = cur.fetchall()

                if rows:
                    print(f"\n📄 Sample Data (first {min(25, len(rows))} rows):")
                    print()

                    # Format data for tabulate
                    headers = list(rows[0].keys())
                    table_data = []
                    for row in rows:
                        formatted_row = [format_value(row[col]) for col in headers]
                        table_data.append(formatted_row)

                    # Print as table
                    print(tabulate(table_data, headers=headers, tablefmt='grid', maxcolwidths=20))

                    # Also show some statistics if numeric columns exist
                    numeric_cols = [col['column_name'] for col in columns
                                  if col['data_type'] in ('integer', 'numeric', 'double precision', 'real', 'bigint')]

                    if numeric_cols:
                        print("\n📈 Basic Statistics:")
                        for col in numeric_cols:
                            try:
                                cur.execute(f"""
                                    SELECT
                                        MIN({col}) as min,
                                        MAX({col}) as max,
                                        AVG({col}) as avg,
                                        COUNT(DISTINCT {col}) as distinct_count
                                    FROM public.otpr
                                """)
                                stats = cur.fetchone()
                                print(f"\n   {col}:")
                                print(f"     • Min: {format_value(stats['min'])}")
                                print(f"     • Max: {format_value(stats['max'])}")
                                print(f"     • Avg: {format_value(stats['avg'])}")
                                print(f"     • Distinct: {stats['distinct_count']:,}")
                            except:
                                pass

                else:
                    print("   (No data in this view)")

            except psycopg2.errors.InsufficientPrivilege as e:
                print(f"\n❌ Permission denied: Cannot read from view 'otpr'")
                print(f"   Error: {e}")
            except Exception as e:
                print(f"\n❌ Error reading view: {e}")
                import traceback
                traceback.print_exc()

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