#!/usr/bin/env python3
"""Check and diagnose the sequence issue."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import psycopg2

# Load environment variables
env_path = Path(__file__).parent / '.env.local'
if env_path.exists():
    load_dotenv(env_path)

def check_sequence():
    """Check the sequence status."""
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT", 5432)),
            database=os.getenv("DB_NAME", "databricks_postgres"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            sslmode="require"
        )

        with conn.cursor() as cursor:
            print("🔍 Checking transaction_id sequence...")

            # Check max transaction_id
            cursor.execute("SELECT MAX(transaction_id) as max_id FROM inventory_transactions")
            max_id = cursor.fetchone()[0]
            print(f"   Current MAX(transaction_id): {max_id}")

            # Check sequence name
            cursor.execute("""
                SELECT pg_get_serial_sequence('inventory_transactions', 'transaction_id')
            """)
            seq_result = cursor.fetchone()

            if seq_result and seq_result[0]:
                seq_name = seq_result[0]
                print(f"   Sequence name: {seq_name}")

                # Get current sequence value
                cursor.execute(f"SELECT last_value FROM {seq_name}")
                last_val = cursor.fetchone()[0]
                print(f"   Sequence last_value: {last_val}")

                # Check if sequence is behind
                if last_val < max_id:
                    print(f"   ⚠️ ISSUE: Sequence ({last_val}) is behind MAX ID ({max_id})")
                    print(f"   This will cause duplicate key errors!")
                else:
                    print(f"   ✅ Sequence is properly ahead of MAX ID")

            else:
                print("   ⚠️ No sequence found - might be using IDENTITY column")

            # Check for low transaction_ids that might conflict
            cursor.execute("""
                SELECT transaction_id
                FROM inventory_transactions
                WHERE transaction_id < 100
                ORDER BY transaction_id
            """)
            low_ids = cursor.fetchall()
            if low_ids:
                print(f"\n   ⚠️ Found {len(low_ids)} transactions with ID < 100:")
                for row in low_ids[:10]:  # Show first 10
                    print(f"      - transaction_id: {row[0]}")

        conn.close()

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    check_sequence()