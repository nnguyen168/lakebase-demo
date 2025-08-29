#!/usr/bin/env python3
"""Comprehensive permission check for Lakebase PostgreSQL."""

import os
import sys
from pathlib import Path
import psycopg2
from psycopg2.extras import RealDictCursor

# Load environment variables
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / '.env.local'
load_dotenv(env_path)

def check_all_permissions():
    """Check all database permissions comprehensively."""
    
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT", "5432")
    database = os.getenv("DB_NAME")
    username = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    
    print("=" * 60)
    print("COMPREHENSIVE PERMISSION CHECK")
    print("=" * 60)
    print(f"Host: {host}")
    print(f"Database: {database}")
    print(f"User: {username}")
    print("=" * 60)
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
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # 1. Check user privileges
        print("1. USER PRIVILEGES:")
        print("-" * 40)
        cursor.execute("""
            SELECT 
                has_database_privilege(current_user, current_database(), 'CREATE') as can_create,
                has_database_privilege(current_user, current_database(), 'CONNECT') as can_connect,
                has_database_privilege(current_user, current_database(), 'TEMP') as can_temp
        """)
        privs = cursor.fetchone()
        for key, value in privs.items():
            print(f"  {key}: {value}")
        print()
        
        # 2. Check schema privileges
        print("2. SCHEMA PRIVILEGES:")
        print("-" * 40)
        cursor.execute("""
            SELECT 
                nspname as schema_name,
                has_schema_privilege(current_user, nspname, 'CREATE') as can_create,
                has_schema_privilege(current_user, nspname, 'USAGE') as can_use
            FROM pg_namespace
            WHERE nspname NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
            ORDER BY nspname
        """)
        schemas = cursor.fetchall()
        for schema in schemas:
            print(f"  Schema: {schema['schema_name']}")
            print(f"    Can create objects: {schema['can_create']}")
            print(f"    Can use: {schema['can_use']}")
        print()
        
        # 3. Check all schemas (including ones we might own)
        print("3. ALL AVAILABLE SCHEMAS:")
        print("-" * 40)
        cursor.execute("""
            SELECT 
                schema_name,
                schema_owner
            FROM information_schema.schemata
            WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
            ORDER BY schema_name
        """)
        all_schemas = cursor.fetchall()
        for schema in all_schemas:
            print(f"  {schema['schema_name']} (owner: {schema['schema_owner']})")
        print()
        
        # 4. Check if we own any schemas
        print("4. SCHEMAS OWNED BY CURRENT USER:")
        print("-" * 40)
        cursor.execute("""
            SELECT 
                schema_name
            FROM information_schema.schemata
            WHERE schema_owner = current_user
            ORDER BY schema_name
        """)
        owned_schemas = cursor.fetchall()
        if owned_schemas:
            for schema in owned_schemas:
                print(f"  - {schema['schema_name']}")
        else:
            print("  None")
        print()
        
        # 5. Check table creation in different schemas
        print("5. TABLE CREATION TEST:")
        print("-" * 40)
        
        # Try creating in public
        test_results = []
        schemas_to_test = ['public']
        
        # Add any owned schemas
        for schema in owned_schemas:
            schemas_to_test.append(schema['schema_name'])
        
        # Also try user-specific schema names
        user_prefix = username.split('@')[0].replace('.', '_')
        potential_schemas = [
            user_prefix,
            f"{user_prefix}_db",
            f"{user_prefix}_schema",
            'inventory_demo',
            'demo'
        ]
        
        for potential in potential_schemas:
            cursor.execute("""
                SELECT schema_name 
                FROM information_schema.schemata 
                WHERE schema_name = %s
            """, (potential,))
            if cursor.fetchone():
                schemas_to_test.append(potential)
        
        for schema in set(schemas_to_test):
            try:
                test_table = f"{schema}.test_permission_check"
                cursor.execute(f"""
                    CREATE TABLE {test_table} (
                        id SERIAL PRIMARY KEY,
                        test VARCHAR(10)
                    )
                """)
                conn.commit()
                
                # If successful, drop it
                cursor.execute(f"DROP TABLE {test_table}")
                conn.commit()
                
                test_results.append(f"  ✓ Can create tables in schema: {schema}")
            except Exception as e:
                conn.rollback()
                test_results.append(f"  ✗ Cannot create in {schema}: {str(e).split('DETAIL')[0].strip()}")
        
        for result in test_results:
            print(result)
        print()
        
        # 6. Check existing tables we can access
        print("6. ACCESSIBLE TABLES:")
        print("-" * 40)
        cursor.execute("""
            SELECT 
                table_schema,
                table_name,
                table_type
            FROM information_schema.tables
            WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
            ORDER BY table_schema, table_name
        """)
        tables = cursor.fetchall()
        current_schema = None
        for table in tables:
            if table['table_schema'] != current_schema:
                current_schema = table['table_schema']
                print(f"  Schema: {current_schema}")
            print(f"    - {table['table_name']} ({table['table_type']})")
        print()
        
        # 7. Check grants on existing tables
        print("7. PERMISSIONS ON EXISTING TABLES:")
        print("-" * 40)
        cursor.execute("""
            SELECT 
                table_schema,
                table_name,
                privilege_type
            FROM information_schema.table_privileges
            WHERE grantee = current_user
            ORDER BY table_schema, table_name, privilege_type
        """)
        grants = cursor.fetchall()
        if grants:
            current_table = None
            for grant in grants:
                table_full = f"{grant['table_schema']}.{grant['table_name']}"
                if table_full != current_table:
                    current_table = table_full
                    print(f"  {current_table}:")
                print(f"    - {grant['privilege_type']}")
        else:
            print("  No explicit table permissions found")
        
        cursor.close()
        conn.close()
        
        print()
        print("=" * 60)
        print("RECOMMENDATION:")
        print("=" * 60)
        
        # Provide recommendation based on findings
        if any("✓ Can create tables" in r for r in test_results):
            schema_name = [r.split("schema: ")[1] for r in test_results if "✓" in r][0]
            print(f"✅ You CAN create tables in schema: {schema_name}")
            print(f"   Update your configuration to use this schema.")
        else:
            print("❌ You CANNOT create tables in any available schema.")
            print("   You need to request permissions from your Databricks admin:")
            print("   1. Grant CREATE privilege on the public schema, OR")
            print("   2. Create a dedicated schema for your user with full permissions")
            print()
            print("   SQL commands for admin to run:")
            print(f"   GRANT CREATE ON SCHEMA public TO \"{username}\";")
            print("   -- OR --")
            print(f"   CREATE SCHEMA IF NOT EXISTS {user_prefix}_inventory;")
            print(f"   GRANT ALL ON SCHEMA {user_prefix}_inventory TO \"{username}\";")
        
    except Exception as e:
        print(f"Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = check_all_permissions()
    sys.exit(0 if success else 1)