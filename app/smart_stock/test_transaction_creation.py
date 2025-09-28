#!/usr/bin/env python3
"""Test script to verify transaction creation in the inventory_transactions table."""

import os
import sys
import json
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

# Load environment variables
env_path = Path(__file__).parent / '.env.local'
if env_path.exists():
    load_dotenv(env_path)
    print(f"✅ Loaded environment from {env_path}")

# API base URL
API_BASE_URL = "http://localhost:8000"

def test_direct_db_connection():
    """Test direct database connection and query."""
    print("\n🔍 Testing direct database connection...")

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
            # Check current transaction count
            cursor.execute("SELECT COUNT(*) as count FROM inventory_transactions")
            result = cursor.fetchone()
            print(f"✅ Database connected! Current transaction count: {result['count']}")

            # Get sample products and warehouses for testing
            cursor.execute("SELECT product_id, name FROM products LIMIT 3")
            products = cursor.fetchall()
            print(f"📦 Sample products: {[p['name'] for p in products]}")

            cursor.execute("SELECT warehouse_id, name FROM warehouses LIMIT 3")
            warehouses = cursor.fetchall()
            print(f"🏭 Sample warehouses: {[w['name'] for w in warehouses]}")

        conn.close()
        return products, warehouses

    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return None, None

def test_create_transaction_api(product_id, warehouse_id):
    """Test creating a transaction via the API."""
    print(f"\n🚀 Testing transaction creation via API...")

    # Prepare transaction data
    transaction_data = {
        "product_id": product_id,
        "warehouse_id": warehouse_id,
        "quantity_change": 50,
        "transaction_type": "inbound",
        "notes": f"Test transaction created at {datetime.now().isoformat()}"
    }

    print(f"📝 Creating transaction: {json.dumps(transaction_data, indent=2)}")

    try:
        # Make POST request to create transaction
        response = requests.post(
            f"{API_BASE_URL}/api/transactions/",
            json=transaction_data,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            transaction = response.json()
            print(f"✅ Transaction created successfully!")
            print(f"   Transaction ID: {transaction.get('transaction_id')}")
            print(f"   Transaction Number: {transaction.get('transaction_number')}")
            print(f"   Status: {transaction.get('status')}")
            print(f"   Timestamp: {transaction.get('transaction_timestamp')}")
            return transaction
        else:
            print(f"❌ Failed to create transaction: {response.status_code}")
            print(f"   Error: {response.text}")
            return None

    except Exception as e:
        print(f"❌ API request failed: {str(e)}")
        return None

def verify_transaction_in_db(transaction_number):
    """Verify the transaction exists in the database."""
    print(f"\n🔍 Verifying transaction in database...")

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
            # Query for the specific transaction
            cursor.execute("""
                SELECT
                    t.transaction_id,
                    t.transaction_number,
                    t.quantity_change,
                    t.transaction_type,
                    t.status,
                    t.notes,
                    t.transaction_timestamp,
                    p.name as product_name,
                    w.name as warehouse_name
                FROM inventory_transactions t
                JOIN products p ON t.product_id = p.product_id
                JOIN warehouses w ON t.warehouse_id = w.warehouse_id
                WHERE t.transaction_number = %s
            """, (transaction_number,))

            result = cursor.fetchone()

            if result:
                print(f"✅ Transaction verified in database!")
                print(f"   Database Record:")
                print(f"   - ID: {result['transaction_id']}")
                print(f"   - Number: {result['transaction_number']}")
                print(f"   - Product: {result['product_name']}")
                print(f"   - Warehouse: {result['warehouse_name']}")
                print(f"   - Quantity: {result['quantity_change']}")
                print(f"   - Type: {result['transaction_type']}")
                print(f"   - Status: {result['status']}")
                print(f"   - Notes: {result['notes']}")
                return True
            else:
                print(f"❌ Transaction not found in database!")
                return False

        conn.close()

    except Exception as e:
        print(f"❌ Database verification failed: {str(e)}")
        return False

def test_get_transactions_api():
    """Test fetching transactions via the API."""
    print(f"\n📋 Testing fetch transactions via API...")

    try:
        response = requests.get(f"{API_BASE_URL}/api/transactions/?limit=5")

        if response.status_code == 200:
            data = response.json()
            transactions = data.get('items', [])
            pagination = data.get('pagination', {})

            print(f"✅ Successfully fetched transactions!")
            print(f"   Total transactions: {pagination.get('total', 0)}")
            print(f"   Fetched: {len(transactions)} transactions")

            if transactions:
                print(f"\n   Latest transactions:")
                for t in transactions[:3]:
                    print(f"   - {t.get('transaction_number')} | {t.get('product')} | {t.get('quantity_change')} | {t.get('status')}")

            return True
        else:
            print(f"❌ Failed to fetch transactions: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ API request failed: {str(e)}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("🧪 TRANSACTION CREATION TEST SUITE")
    print("=" * 60)

    # Test 1: Direct database connection
    products, warehouses = test_direct_db_connection()

    if not products or not warehouses:
        print("\n❌ Cannot proceed without database connection")
        return 1

    # Test 2: Create transaction via API
    product_id = products[0]['product_id']
    warehouse_id = warehouses[0]['warehouse_id']

    transaction = test_create_transaction_api(product_id, warehouse_id)

    if not transaction:
        print("\n⚠️  Transaction creation via API failed")
        return 1

    # Test 3: Verify transaction in database
    transaction_number = transaction.get('transaction_number')
    if transaction_number:
        verified = verify_transaction_in_db(transaction_number)

        if not verified:
            print("\n⚠️  Transaction not verified in database")
            return 1

    # Test 4: Fetch transactions via API
    test_get_transactions_api()

    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)
    return 0

if __name__ == "__main__":
    sys.exit(main())