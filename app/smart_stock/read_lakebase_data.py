#!/usr/bin/env python3
"""Read and display data from Lakebase PostgreSQL database."""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from tabulate import tabulate
from datetime import datetime
from decimal import Decimal
from dotenv import load_dotenv

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
        return "NULL"
    return value

def get_table_list(conn):
    """Get list of all tables in the database."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT tablename
            FROM pg_tables
            WHERE schemaname = 'public'
            ORDER BY tablename
        """)
        return [row[0] for row in cur.fetchall()]

def get_table_count(conn, table_name):
    """Get row count for a table."""
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) FROM {table_name}")
            return cur.fetchone()[0]
    except psycopg2.errors.InsufficientPrivilege:
        return "No Access"
    except Exception as e:
        return f"Error: {str(e)}"

def read_table_data(conn, table_name, limit=10):
    """Read data from a specific table."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # Get column info
        cur.execute(f"""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = '{table_name}'
            ORDER BY ordinal_position
        """)
        columns = cur.fetchall()

        # Get sample data
        cur.execute(f"SELECT * FROM {table_name} ORDER BY 1 LIMIT {limit}")
        rows = cur.fetchall()

        return columns, rows

def main():
    """Main function to read and display database data."""
    print("🔌 Connecting to Lakebase PostgreSQL Database...")
    print(f"   Host: {DB_CONFIG['host']}")
    print(f"   Database: {DB_CONFIG['database']}")
    print(f"   User: {DB_CONFIG['user']}")
    print()

    try:
        # Connect to database
        conn = psycopg2.connect(**DB_CONFIG)
        print("✅ Successfully connected to database!\n")

        # Get list of tables
        tables = get_table_list(conn)

        if not tables:
            print("⚠️  No tables found in the database.")
            return

        print(f"📊 Found {len(tables)} tables in the database:\n")

        # Display table summary
        table_summary = []
        for table in tables:
            count = get_table_count(conn, table)
            table_summary.append([table, count])

        print(tabulate(table_summary, headers=["Table Name", "Row Count"], tablefmt="grid"))
        print()

        # Display data from each table
        for table in tables:
            count = get_table_count(conn, table)
            print(f"\n{'='*80}")
            print(f"📋 Table: {table} (Total rows: {count})")
            print(f"{'='*80}")

            if count == 0:
                print("   (No data in this table)")
                continue

            if isinstance(count, str):  # Permission error or other error
                print(f"   ⚠️  {count}")
                continue

            try:
                columns, rows = read_table_data(conn, table)
            except psycopg2.errors.InsufficientPrivilege:
                print("   ⚠️  No permission to read this table")
                continue
            except Exception as e:
                print(f"   ⚠️  Error reading table: {e}")
                continue

            # Display column information
            print("\n📝 Columns:")
            col_info = [[col['column_name'], col['data_type']] for col in columns]
            print(tabulate(col_info, headers=["Column Name", "Data Type"], tablefmt="simple"))

            # Display sample data
            print(f"\n📄 Sample Data (showing up to 10 rows):")
            if rows:
                # Format data for display
                formatted_rows = []
                for row in rows:
                    formatted_row = {k: format_value(v) for k, v in row.items()}
                    formatted_rows.append(formatted_row)

                # Convert to list of lists for tabulate
                headers = list(rows[0].keys())
                data = [[row[h] for h in headers] for row in formatted_rows]

                print(tabulate(data, headers=headers, tablefmt="grid", maxcolwidths=30))
            else:
                print("   (No data to display)")

        # Close connection
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