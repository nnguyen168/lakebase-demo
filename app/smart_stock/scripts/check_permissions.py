#!/usr/bin/env python3
"""Check database permissions and schemas."""

import os
import sys
from pathlib import Path
import psycopg2

# Load environment variables
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / '.env.local'
load_dotenv(env_path)

def check_permissions():
    """Check database permissions and available schemas."""
    
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT", "5432")
    database = os.getenv("DB_NAME")
    username = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    
    print("Checking database permissions...")
    print(f"User: {username}")
    print(f"Database: {database}")
    print()
    
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=username,
            password=password,
            sslmode="require"
        )
        cursor = conn.cursor()
        
        # Check current user
        cursor.execute("SELECT current_user, session_user")
        users = cursor.fetchone()
        print(f"Current user: {users[0]}")
        print(f"Session user: {users[1]}")
        print()
        
        # List available schemas
        cursor.execute("""
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_owner = current_user
            OR schema_name IN ('public', 'inventory_demo')
            ORDER BY schema_name
        """)
        schemas = cursor.fetchall()
        print("Available schemas:")
        for schema in schemas:
            print(f"  - {schema[0]}")
        print()
        
        # Check if we can create schemas
        cursor.execute("""
            SELECT has_database_privilege(current_user, current_database(), 'CREATE')
        """)
        can_create = cursor.fetchone()[0]
        print(f"Can create schemas: {can_create}")
        print()
        
        # Check if we can create tables in public schema with a prefix
        table_prefix = "nam_nguyen_"
        print(f"Attempting to create table with prefix: {table_prefix}")
        try:
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {table_prefix}test_table (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100)
                )
            """)
            conn.commit()
            print(f"✓ Successfully created test table: {table_prefix}test_table")
            
            # Clean up test table
            cursor.execute(f"DROP TABLE IF EXISTS {table_prefix}test_table")
            conn.commit()
            print(f"✓ Cleaned up test table")
            
            print()
            print(f"RECOMMENDATION: Use table prefix '{table_prefix}' for your tables")
            print("Tables will be created as:")
            print(f"  - {table_prefix}customers")
            print(f"  - {table_prefix}products")
            print(f"  - {table_prefix}orders")
            print(f"  - {table_prefix}inventory_history")
            print(f"  - {table_prefix}inventory_forecast")
            
        except Exception as e:
            print(f"✗ Cannot create tables in public schema: {e}")
            conn.rollback()
            
            # Check what we CAN do
            print("\nChecking existing permissions...")
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                LIMIT 5
            """)
            tables = cursor.fetchall()
            print("Existing tables in public schema:")
            for table in tables:
                print(f"  - {table[0]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = check_permissions()
    sys.exit(0 if success else 1)