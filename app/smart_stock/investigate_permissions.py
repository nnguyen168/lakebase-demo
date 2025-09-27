#!/usr/bin/env python3
"""Investigate database permissions for the OTPR view."""

import psycopg2
from psycopg2.extras import RealDictCursor
from tabulate import tabulate

# Database configuration
DB_CONFIG = {
    "host": "instance-9965ce63-150c-4746-93dc-a3dcb78fda3b.database.cloud.databricks.com",
    "port": "5432",
    "database": "databricks_postgres",
    "user": "lakebase_demo_app",
    "password": "lakebasedemo2025",
}

def investigate_permissions():
    """Investigate why we can't access the OTPR view."""
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = True

    print("🔍 DATABASE PERMISSION INVESTIGATION")
    print("="*70)

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # 1. Check current user
        print("\n1️⃣ CURRENT CONNECTION INFO:")
        cur.execute("SELECT current_user, current_database(), version()")
        info = cur.fetchone()
        print(f"   User: {info['current_user']}")
        print(f"   Database: {info['current_database']}")
        print(f"   PostgreSQL: {info['version'].split(',')[0]}")

        # 2. Check view ownership
        print("\n2️⃣ VIEW OWNERSHIP:")
        cur.execute("""
            SELECT
                schemaname,
                viewname,
                viewowner,
                definition IS NOT NULL as has_definition
            FROM pg_views
            WHERE viewname = 'otpr'
        """)
        views = cur.fetchall()
        if views:
            for v in views:
                print(f"   Schema: {v['schemaname']}")
                print(f"   View: {v['viewname']}")
                print(f"   Owner: {v['viewowner']}")
                print(f"   Has Definition: {v['has_definition']}")
        else:
            print("   ❌ View 'otpr' not found in pg_views")

        # 3. Check explicit permissions on the view
        print("\n3️⃣ EXPLICIT PERMISSIONS ON 'otpr' VIEW:")
        cur.execute("""
            SELECT
                grantee,
                privilege_type,
                is_grantable
            FROM information_schema.table_privileges
            WHERE table_name = 'otpr'
            ORDER BY grantee, privilege_type
        """)
        privs = cur.fetchall()
        if privs:
            data = [[p['grantee'], p['privilege_type'], p['is_grantable']] for p in privs]
            print(tabulate(data, headers=['Grantee', 'Privilege', 'Grantable'], tablefmt='grid'))
        else:
            print("   ❌ No explicit permissions found for 'otpr' view")

        # 4. Check our user's privileges
        print("\n4️⃣ CURRENT USER PRIVILEGES:")
        cur.execute("""
            SELECT
                privilege_type,
                COUNT(*) as count
            FROM information_schema.table_privileges
            WHERE grantee = current_user
            GROUP BY privilege_type
            ORDER BY privilege_type
        """)
        user_privs = cur.fetchall()
        if user_privs:
            for p in user_privs:
                print(f"   • {p['privilege_type']}: {p['count']} objects")
        else:
            print("   ❌ No explicit privileges found for current user")

        # 5. Check schema permissions
        print("\n5️⃣ SCHEMA PERMISSIONS:")
        cur.execute("""
            SELECT
                nspname as schema_name,
                nspacl as access_privileges
            FROM pg_namespace
            WHERE nspname IN ('public', 'information_schema')
        """)
        schemas = cur.fetchall()
        for s in schemas:
            print(f"   Schema: {s['schema_name']}")
            print(f"   ACL: {s['access_privileges'] or 'Default (no explicit ACL)'}")

        # 6. Check if we can see the view definition
        print("\n6️⃣ VIEW DEFINITION ACCESS:")
        try:
            cur.execute("SELECT pg_get_viewdef('public.otpr'::regclass, true)")
            definition = cur.fetchone()
            if definition:
                print("   ✅ Can read view definition (surprising given SELECT permission denied)")
                print("   This suggests the view exists but has restricted SELECT permissions")
        except Exception as e:
            print(f"   ❌ Cannot read view definition: {e}")

        # 7. Check tables we CAN access
        print("\n7️⃣ TABLES/VIEWS WE CAN ACCESS:")
        accessible = []

        # Check tables
        cur.execute("""
            SELECT tablename as name, 'table' as type
            FROM pg_tables
            WHERE schemaname = 'public'
        """)
        tables = cur.fetchall()

        for t in tables:
            try:
                cur.execute(f"SELECT COUNT(*) FROM {t['name']} LIMIT 1")
                accessible.append(f"✅ {t['name']} (table)")
            except:
                accessible.append(f"❌ {t['name']} (table)")

        # Check views
        cur.execute("""
            SELECT viewname as name
            FROM pg_views
            WHERE schemaname = 'public'
        """)
        views = cur.fetchall()

        for v in views:
            try:
                cur.execute(f"SELECT COUNT(*) FROM {v['name']} LIMIT 1")
                accessible.append(f"✅ {v['name']} (view)")
            except:
                accessible.append(f"❌ {v['name']} (view)")

        for item in accessible:
            print(f"   {item}")

        # 8. Check role membership
        print("\n8️⃣ ROLE MEMBERSHIP:")
        cur.execute("""
            SELECT
                r.rolname as role_name,
                r.rolsuper as is_superuser,
                r.rolinherit as can_inherit,
                r.rolcreaterole as can_create_role,
                r.rolcreatedb as can_create_db
            FROM pg_roles r
            WHERE r.rolname = current_user
        """)
        role = cur.fetchone()
        if role:
            print(f"   Role: {role['role_name']}")
            print(f"   Superuser: {role['is_superuser']}")
            print(f"   Can Inherit: {role['can_inherit']}")
            print(f"   Can Create Role: {role['can_create_role']}")
            print(f"   Can Create DB: {role['can_create_db']}")

        # 9. Check parent roles
        cur.execute("""
            SELECT
                r.rolname as parent_role
            FROM pg_roles r
            JOIN pg_auth_members m ON r.oid = m.roleid
            JOIN pg_roles u ON u.oid = m.member
            WHERE u.rolname = current_user
        """)
        parent_roles = cur.fetchall()
        if parent_roles:
            print("\n   Parent Roles:")
            for pr in parent_roles:
                print(f"   • {pr['parent_role']}")
        else:
            print("\n   No parent roles (not member of any role)")

    conn.close()

    print("\n" + "="*70)
    print("📋 DIAGNOSIS:")
    print()
    print("The permission issue occurs because:")
    print("1. The view 'otpr' is owned by 'nam.nguyen@databricks.com'")
    print("2. The app connects as 'lakebase_demo_app'")
    print("3. No explicit SELECT permission was granted to 'lakebase_demo_app'")
    print()
    print("In PostgreSQL, only the owner and superusers can access an object")
    print("unless explicit permissions are granted.")
    print()
    print("🔧 SOLUTIONS:")
    print()
    print("1. GRANT PERMISSION (Run as nam.nguyen@databricks.com):")
    print("   GRANT SELECT ON public.otpr TO lakebase_demo_app;")
    print()
    print("2. CHANGE VIEW OWNER (Run as nam.nguyen@databricks.com):")
    print("   ALTER VIEW public.otpr OWNER TO lakebase_demo_app;")
    print()
    print("3. CREATE A COPY (Run as lakebase_demo_app):")
    print("   CREATE VIEW otpr_copy AS (SELECT * FROM inventory_transactions ...);")
    print()
    print("4. USE PUBLIC ROLE:")
    print("   GRANT SELECT ON public.otpr TO PUBLIC;")
    print("="*70)

if __name__ == "__main__":
    investigate_permissions()