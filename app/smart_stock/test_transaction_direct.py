#!/usr/bin/env python3
"""Test transaction creation directly without relying on sequence."""

import os
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

# Load environment variables
env_path = Path(__file__).parent / '.env.local'
if env_path.exists():
    load_dotenv(env_path)

def test_direct_insert():
    """Test direct insert with calculated ID."""
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT", 5432)),
            database=os.getenv("DB_NAME", "databricks_postgres"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            sslmode="require"
        )

        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Get max ID
            cursor.execute("SELECT COALESCE(MAX(transaction_id), 0) + 1 as next_id FROM inventory_transactions")
            next_id = cursor.fetchone()['next_id']
            print(f"Next available ID: {next_id}")

            # Generate transaction number
            transaction_number = f"TEST-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

            # Insert with explicit ID
            cursor.execute("""
                INSERT INTO inventory_transactions (
                    transaction_id,
                    transaction_number,
                    product_id,
                    warehouse_id,
                    quantity_change,
                    transaction_type,
                    status,
                    notes,
                    transaction_timestamp,
                    updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """, (
                next_id,
                transaction_number,
                1,  # product_id
                1,  # warehouse_id
                100,  # quantity_change
                'inbound',
                'pending',
                'Direct test transaction',
            ))

            conn.commit()
            print(f"✅ Successfully inserted transaction with ID {next_id}")

            # Verify it was inserted
            cursor.execute("""
                SELECT t.*, p.name as product_name, w.name as warehouse_name
                FROM inventory_transactions t
                JOIN products p ON t.product_id = p.product_id
                JOIN warehouses w ON t.warehouse_id = w.warehouse_id
                WHERE t.transaction_id = %s
            """, (next_id,))

            result = cursor.fetchone()
            if result:
                print(f"✅ Verified transaction in database:")
                print(f"   - Number: {result['transaction_number']}")
                print(f"   - Product: {result['product_name']}")
                print(f"   - Warehouse: {result['warehouse_name']}")
                print(f"   - Quantity: {result['quantity_change']}")
                print(f"   - Status: {result['status']}")

        conn.close()
        return True

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_direct_insert()
    sys.exit(0 if success else 1)