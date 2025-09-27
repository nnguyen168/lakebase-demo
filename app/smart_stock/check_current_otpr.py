#!/usr/bin/env python3
"""Check current OTPR values in the database."""

import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

# Database configuration
DB_CONFIG = {
    "host": "instance-9965ce63-150c-4746-93dc-a3dcb78fda3b.database.cloud.databricks.com",
    "port": "5432",
    "database": "databricks_postgres",
    "user": "lakebase_demo_app",
    "password": "lakebasedemo2025",
}

def check_otpr():
    """Check OTPR values from different sources."""
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = True

    print(f"🕒 Checking at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # Try to read from OTPR view
        print("\n1️⃣ Attempting to read from OTPR view:")
        try:
            cur.execute("SELECT * FROM public.otpr")
            result = cur.fetchone()
            if result:
                print("✅ OTPR View Data:")
                for key, value in result.items():
                    print(f"   {key}: {value}")
            else:
                print("❌ View returned no data")
        except Exception as e:
            print(f"❌ Cannot access view: {e}")

        # Calculate from inventory_transactions
        print("\n2️⃣ Calculating from inventory_transactions table:")
        query = """
        WITH simple_metrics AS (
            SELECT
                COUNT(CASE
                    WHEN DATE(transaction_timestamp) > CURRENT_DATE - INTERVAL '30 days'
                    AND transaction_type = 'sale'
                    THEN 1
                END) as current_orders,
                COUNT(CASE
                    WHEN DATE(transaction_timestamp) > CURRENT_DATE - INTERVAL '30 days'
                    AND transaction_type = 'sale'
                    AND status = 'delivered'
                    THEN 1
                END) as current_on_time,
                COUNT(CASE
                    WHEN DATE(transaction_timestamp) > CURRENT_DATE - INTERVAL '60 days'
                    AND DATE(transaction_timestamp) <= CURRENT_DATE - INTERVAL '30 days'
                    AND transaction_type = 'sale'
                    THEN 1
                END) as previous_orders,
                COUNT(CASE
                    WHEN DATE(transaction_timestamp) > CURRENT_DATE - INTERVAL '60 days'
                    AND DATE(transaction_timestamp) <= CURRENT_DATE - INTERVAL '30 days'
                    AND transaction_type = 'sale'
                    AND status = 'delivered'
                    THEN 1
                END) as previous_on_time
            FROM inventory_transactions
            WHERE transaction_timestamp >= CURRENT_DATE - INTERVAL '60 days'
        )
        SELECT
            current_orders,
            current_on_time,
            previous_orders,
            previous_on_time,
            ROUND(100.0 * current_on_time::numeric / NULLIF(current_orders, 0)::numeric, 1) as otpr_last_30d,
            ROUND(100.0 * previous_on_time::numeric / NULLIF(previous_orders, 0)::numeric, 1) as otpr_prev_30d,
            ROUND(100.0 * current_on_time::numeric / NULLIF(current_orders, 0)::numeric, 1) -
            ROUND(100.0 * previous_on_time::numeric / NULLIF(previous_orders, 0)::numeric, 1) as change_ppt
        FROM simple_metrics
        """

        cur.execute(query)
        result = cur.fetchone()
        if result:
            print("✅ Calculated OTPR Data:")
            print(f"   Current period: {result['current_orders']} orders, {result['current_on_time']} on-time")
            print(f"   Previous period: {result['previous_orders']} orders, {result['previous_on_time']} on-time")
            print(f"   ---")
            print(f"   OTPR Last 30d: {result['otpr_last_30d']}%")
            print(f"   OTPR Prev 30d: {result['otpr_prev_30d']}%")
            print(f"   Change: {result['change_ppt']} percentage points")

            # Determine trend
            if result['change_ppt'] > 0:
                trend = '↑'
            elif result['change_ppt'] < 0:
                trend = '↓'
            else:
                trend = '→'
            print(f"   Trend: {trend}")

    conn.close()
    print("\n" + "="*60)
    print("✅ Check complete")

if __name__ == "__main__":
    check_otpr()