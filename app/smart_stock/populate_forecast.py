#!/usr/bin/env python
"""Populate inventory_forecast table with sample data based on transactions."""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from pathlib import Path
import random

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
conn = psycopg2.connect(**db_config, cursor_factory=RealDictCursor)
cursor = conn.cursor()

try:
    # Clear existing forecast data
    cursor.execute("DELETE FROM inventory_forecast")

    # Get all products and warehouses
    cursor.execute("SELECT product_id FROM products")
    products = cursor.fetchall()

    cursor.execute("SELECT warehouse_id FROM warehouses")
    warehouses = cursor.fetchall()

    print(f"Found {len(products)} products and {len(warehouses)} warehouses")

    # Create forecast for each product-warehouse combination
    for product in products:
        for warehouse in warehouses:
            # Calculate current stock from transactions
            cursor.execute("""
                SELECT
                    COALESCE(SUM(CASE
                        WHEN transaction_type = 'inbound' THEN quantity_change
                        WHEN transaction_type = 'sale' THEN quantity_change
                        ELSE quantity_change
                    END), 0) as current_stock
                FROM inventory_transactions
                WHERE product_id = %s AND warehouse_id = %s
            """, (product['product_id'], warehouse['warehouse_id']))

            result = cursor.fetchone()
            current_stock = max(0, result['current_stock'] if result else 0)

            # Generate forecast data
            # Base demand on historical sales (if any)
            cursor.execute("""
                SELECT
                    COUNT(*) as transaction_count,
                    COALESCE(AVG(ABS(quantity_change)), 10) as avg_quantity
                FROM inventory_transactions
                WHERE product_id = %s
                AND warehouse_id = %s
                AND transaction_type = 'sale'
            """, (product['product_id'], warehouse['warehouse_id']))

            sales_data = cursor.fetchone()
            avg_daily_demand = float(sales_data['avg_quantity']) if sales_data['transaction_count'] > 0 else random.uniform(5, 20)

            # Calculate forecast values
            forecast_30_days = int(avg_daily_demand * 30 * random.uniform(0.8, 1.3))  # Add some variability
            reorder_point = int(avg_daily_demand * 14)  # 14 days lead time
            reorder_quantity = int(avg_daily_demand * 30)  # Order for 30 days
            confidence_score = min(0.95, 0.7 + (sales_data['transaction_count'] * 0.01))  # Higher confidence with more data

            # Determine status based on current stock
            if current_stock == 0:
                status = 'expired'  # Out of stock
            elif current_stock < reorder_point:
                status = 'pending'  # Need to reorder
            else:
                status = 'active'  # Good stock level

            # Insert forecast record
            cursor.execute("""
                INSERT INTO inventory_forecast (
                    product_id, warehouse_id, current_stock, forecast_30_days,
                    reorder_point, reorder_quantity, confidence_score, status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                product['product_id'],
                warehouse['warehouse_id'],
                current_stock,
                forecast_30_days,
                reorder_point,
                reorder_quantity,
                confidence_score,
                status
            ))

    conn.commit()

    # Verify the data
    cursor.execute("SELECT COUNT(*) as count FROM inventory_forecast")
    count = cursor.fetchone()
    print(f"\n✅ Successfully created {count['count']} forecast records!")

    # Show sample data
    cursor.execute("""
        SELECT
            p.name as product_name,
            w.name as warehouse_name,
            if.current_stock,
            if.forecast_30_days,
            if.reorder_point,
            if.status
        FROM inventory_forecast if
        JOIN products p ON if.product_id = p.product_id
        JOIN warehouses w ON if.warehouse_id = w.warehouse_id
        LIMIT 10
    """)

    print("\nSample forecast data:")
    for row in cursor.fetchall():
        print(f"  {row['product_name'][:30]} @ {row['warehouse_name'][:25]}: Stock={row['current_stock']}, Forecast={row['forecast_30_days']}, Status={row['status']}")

except Exception as e:
    conn.rollback()
    print(f"❌ Error: {e}")

finally:
    cursor.close()
    conn.close()