#!/usr/bin/env python3
"""Test OTPR view directly in the database."""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent / '.env.local'
if env_path.exists():
    load_dotenv(env_path)

# Database configuration from environment
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "instance-9965ce63-150c-4746-93dc-a3dcb78fda3b.database.cloud.databricks.com"),
    "port": os.getenv("DB_PORT", "5432"),
    "database": os.getenv("DB_NAME", "databricks_postgres"),
    "user": os.getenv("DB_USER", "lakebase_demo_app"),
    "password": os.getenv("DB_PASSWORD", "lakebasedemo2025"),
}

# Get schema from environment
DB_SCHEMA = os.getenv("DB_SCHEMA", "public")

def test_otpr_view():
    """Test the OTPR view directly."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True

        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Try the view first
            try:
                cur.execute(f"SELECT * FROM {DB_SCHEMA}.otpr")
                result = cur.fetchone()
                print("✅ OTPR View Data:")
                for key, value in result.items():
                    print(f"   {key}: {value}")
            except Exception as e:
                print(f"❌ View error: {e}")
                print(f"   Using schema: {DB_SCHEMA}")

                # Try the direct calculation
                print("\n🔄 Calculating from inventory_transactions table:")
                query = """
                WITH simple_metrics AS (
                    SELECT
                        COUNT(CASE
                            WHEN DATE(transaction_timestamp) > CURRENT_DATE - INTERVAL '30 days'
                            THEN 1
                        END) as current_orders,
                        COUNT(CASE
                            WHEN DATE(transaction_timestamp) > CURRENT_DATE - INTERVAL '30 days'
                            AND status = 'delivered'
                            THEN 1
                        END) as current_on_time,
                        COUNT(CASE
                            WHEN DATE(transaction_timestamp) > CURRENT_DATE - INTERVAL '60 days'
                            AND DATE(transaction_timestamp) <= CURRENT_DATE - INTERVAL '30 days'
                            THEN 1
                        END) as previous_orders,
                        COUNT(CASE
                            WHEN DATE(transaction_timestamp) > CURRENT_DATE - INTERVAL '60 days'
                            AND DATE(transaction_timestamp) <= CURRENT_DATE - INTERVAL '30 days'
                            AND status = 'delivered'
                            THEN 1
                        END) as previous_on_time
                    FROM inventory_transactions
                    WHERE transaction_type = 'sale'
                    AND transaction_timestamp >= CURRENT_DATE - INTERVAL '60 days'
                )
                SELECT
                    ROUND(100.0 * current_on_time::numeric / NULLIF(current_orders, 0)::numeric, 1) as otpr_last_30d,
                    ROUND(100.0 * previous_on_time::numeric / NULLIF(previous_orders, 0)::numeric, 1) as otpr_prev_30d
                FROM simple_metrics
                """
                cur.execute(query)
                result = cur.fetchone()
                print("✅ Calculated OTPR Data:")
                for key, value in result.items():
                    print(f"   {key}: {value}")

        conn.close()

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_otpr_view()