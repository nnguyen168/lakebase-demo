#!/usr/bin/env python
"""Test database connection and query actual data."""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path('.env.local')
if env_path.exists():
    load_dotenv(env_path)

# Database configuration
db_config = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "database": os.getenv("DB_NAME", "databricks_postgres"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "sslmode": "require",
}

print("Connecting to database...")
print(f"Host: {db_config['host']}")
print(f"Database: {db_config['database']}")
print(f"User: {db_config['user']}")

try:
    conn = psycopg2.connect(**db_config, cursor_factory=RealDictCursor)
    cursor = conn.cursor()

    print("\n=== CHECKING TABLES ===")
    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)
    tables = cursor.fetchall()
    print("Available tables:")
    for table in tables:
        print(f"  - {table['table_name']}")

    print("\n=== PRODUCTS TABLE ===")
    cursor.execute("SELECT COUNT(*) as count FROM products")
    count = cursor.fetchone()
    print(f"Total products: {count['count']}")

    cursor.execute("SELECT * FROM products LIMIT 5")
    products = cursor.fetchall()
    for p in products:
        print(f"  - {p['name']} (SKU: {p['sku']}, Price: {p['price']})")

    print("\n=== WAREHOUSES TABLE ===")
    cursor.execute("SELECT COUNT(*) as count FROM warehouses")
    count = cursor.fetchone()
    print(f"Total warehouses: {count['count']}")

    cursor.execute("SELECT * FROM warehouses")
    warehouses = cursor.fetchall()
    for w in warehouses:
        print(f"  - {w['name']} (Location: {w['location']}, ID: {w['warehouse_id']})")

    print("\n=== INVENTORY_TRANSACTIONS TABLE ===")
    cursor.execute("SELECT COUNT(*) as count FROM inventory_transactions")
    count = cursor.fetchone()
    print(f"Total transactions: {count['count']}")

    cursor.execute("""
        SELECT it.*, p.name as product_name, w.name as warehouse_name
        FROM inventory_transactions it
        JOIN products p ON it.product_id = p.product_id
        JOIN warehouses w ON it.warehouse_id = w.warehouse_id
        ORDER BY it.transaction_timestamp DESC
        LIMIT 5
    """)
    transactions = cursor.fetchall()
    for t in transactions:
        print(f"  - {t['transaction_number']}: {t['product_name']} @ {t['warehouse_name']} ({t['quantity_change']} units, {t['transaction_type']})")

    print("\n=== INVENTORY_FORECAST TABLE ===")
    cursor.execute("SELECT COUNT(*) as count FROM inventory_forecast")
    count = cursor.fetchone()
    print(f"Total forecast records: {count['count']}")

    cursor.execute("""
        SELECT if.*, p.name as product_name, w.name as warehouse_name
        FROM inventory_forecast if
        JOIN products p ON if.product_id = p.product_id
        JOIN warehouses w ON if.warehouse_id = w.warehouse_id
        LIMIT 5
    """)
    forecasts = cursor.fetchall()
    for f in forecasts:
        print(f"  - {f['product_name']} @ {f['warehouse_name']}: Stock={f['current_stock']}, 30-day forecast={f['forecast_30_days']}")

    cursor.close()
    conn.close()
    print("\n✅ Database connection successful!")

except Exception as e:
    print(f"\n❌ Error: {e}")