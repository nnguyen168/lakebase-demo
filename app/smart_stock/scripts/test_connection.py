#!/usr/bin/env python3
"""Test Lakebase PostgreSQL connection."""

import os
import sys
from pathlib import Path
import psycopg2

# Load environment variables
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / '.env.local'
load_dotenv(env_path)

def test_connection():
    """Test different connection configurations."""
    
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT", "5432")
    database = os.getenv("DB_NAME")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    
    # Also try username without domain
    user_without_domain = user.split('@')[0] if '@' in user else user
    
    print(f"Testing connection to Lakebase:")
    print(f"  Host: {host}")
    print(f"  Port: {port}")
    print(f"  Database: {database}")
    print(f"  User: {user}")
    print(f"  Password: {password[:20]}..." if password else "No password")
    print()
    
    # Test different connection methods
    test_cases = [
        {"user": user, "password": password, "ssl": "require", "desc": "Full email + PAT + SSL"},
        {"user": "token", "password": password, "ssl": "require", "desc": "token user + PAT + SSL"},
        {"user": user, "password": f"token:{password}", "ssl": "require", "desc": "Full email + token:PAT + SSL"},
    ]
    
    for test in test_cases:
        print(f"\nTesting: {test['desc']}...")
        print(f"  User: {test['user']}")
        try:
            conn_string = f"host={host} port={port} dbname={database} user={test['user']} password={test['password']} sslmode={test['ssl']}"
            conn = psycopg2.connect(conn_string)
            cursor = conn.cursor()
            cursor.execute("SELECT version()")
            version = cursor.fetchone()
            print(f"  ✓ Success! PostgreSQL version: {version[0][:50]}...")
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            error_msg = str(e).replace('\n', ' ')
            print(f"  ✗ Failed: {error_msg[:200]}")
    
    return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)