#!/usr/bin/env python3
"""Test Lakebase connection using JDBC-style connection string."""

import os
import sys
from pathlib import Path
import psycopg2
from urllib.parse import urlparse, parse_qs, quote

# Load environment variables
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / '.env.local'
load_dotenv(env_path)

def test_connection():
    """Test connection using JDBC URL format from Databricks."""
    
    # Get credentials from environment
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT", "5432")
    database = os.getenv("DB_NAME")
    username = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    
    username_encoded = quote(username, safe='')  # URL encode the @ symbol
    
    # Build the JDBC-style connection string (without jdbc: prefix for psycopg2)
    jdbc_url = f"postgresql://{host}:{port}/{database}?user={username_encoded}&password={password}&ssl=true&sslmode=require"
    
    print("Testing Lakebase connection with JDBC format...")
    print(f"Connection URL (truncated): {jdbc_url[:100]}...")
    print()
    
    # Method 1: Direct connection string
    print("Method 1: Using full connection URL...")
    try:
        conn = psycopg2.connect(jdbc_url)
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()
        print(f"✓ Success! PostgreSQL version: {version[0][:50]}...")
        
        # Test listing tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            LIMIT 5
        """)
        tables = cursor.fetchall()
        print(f"✓ Found {len(tables)} tables in public schema")
        for table in tables:
            print(f"  - {table[0]}")
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"✗ Failed: {str(e)[:200]}...")
    
    # Method 2: Using individual parameters with SSL
    print("\nMethod 2: Using individual parameters...")
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
        cursor.execute("SELECT current_database()")
        db = cursor.fetchone()
        print(f"✓ Success! Connected to database: {db[0]}")
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"✗ Failed: {str(e)[:200]}...")
    
    return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)