#!/usr/bin/env python3
"""End-to-end test for transaction creation with UI confirmation."""

import os
import sys
import json
import requests
import time
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
FRONTEND_URL = "http://localhost:5173"

def check_services():
    """Check if backend and frontend are running."""
    print("\n🔍 Checking services...")

    # Check backend
    try:
        response = requests.get(f"{API_BASE_URL}/docs")
        if response.status_code == 200:
            print(f"✅ Backend is running at {API_BASE_URL}")
        else:
            print(f"❌ Backend returned status {response.status_code}")
            return False
    except:
        print(f"❌ Backend is not accessible at {API_BASE_URL}")
        print("   Please ensure the server is running with: ./watch.sh")
        return False

    # Check frontend
    try:
        response = requests.get(FRONTEND_URL)
        if response.status_code == 200:
            print(f"✅ Frontend is running at {FRONTEND_URL}")
        else:
            print(f"⚠️ Frontend returned status {response.status_code}")
    except:
        print(f"⚠️ Frontend is not accessible at {FRONTEND_URL}")
        print("   Frontend may not be running. Start with: ./watch.sh")

    return True

def test_full_transaction_flow():
    """Test the complete transaction creation flow."""
    print("\n🚀 Testing full transaction flow...")

    # Step 1: Get current transaction count
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 5432)),
        database=os.getenv("DB_NAME", "databricks_postgres"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        sslmode="require"
    )

    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("SELECT COUNT(*) as count FROM inventory_transactions")
        initial_count = cursor.fetchone()['count']
        print(f"   Initial transaction count: {initial_count}")

    # Step 2: Create a new transaction via API
    transaction_data = {
        "product_id": 5,  # Different product for testing
        "warehouse_id": 2,  # Different warehouse
        "quantity_change": 75,
        "transaction_type": "inbound",
        "notes": f"End-to-end test at {datetime.now().isoformat()}"
    }

    print(f"\n   Creating transaction via API...")
    print(f"   Data: {json.dumps(transaction_data, indent=4)}")

    response = requests.post(
        f"{API_BASE_URL}/api/transactions/",
        json=transaction_data,
        headers={"Content-Type": "application/json"}
    )

    if response.status_code != 200:
        print(f"❌ Failed to create transaction: {response.status_code}")
        print(f"   Error: {response.text}")
        return False

    created_transaction = response.json()
    print(f"\n✅ Transaction created successfully!")
    print(f"   - ID: {created_transaction.get('transaction_id')}")
    print(f"   - Number: {created_transaction.get('transaction_number')}")
    print(f"   - Status: {created_transaction.get('status')}")

    # Step 3: Verify in database
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("""
            SELECT t.*, p.name as product_name, w.name as warehouse_name
            FROM inventory_transactions t
            JOIN products p ON t.product_id = p.product_id
            JOIN warehouses w ON t.warehouse_id = w.warehouse_id
            WHERE t.transaction_id = %s
        """, (created_transaction['transaction_id'],))

        db_record = cursor.fetchone()

        if not db_record:
            print(f"❌ Transaction not found in database!")
            return False

        print(f"\n✅ Transaction verified in database:")
        print(f"   - Product: {db_record['product_name']}")
        print(f"   - Warehouse: {db_record['warehouse_name']}")
        print(f"   - Quantity: {db_record['quantity_change']}")
        print(f"   - Type: {db_record['transaction_type']}")

        # Check final count
        cursor.execute("SELECT COUNT(*) as count FROM inventory_transactions")
        final_count = cursor.fetchone()['count']
        print(f"\n   Final transaction count: {final_count}")
        print(f"   Transactions added: {final_count - initial_count}")

    conn.close()

    # Step 4: Test fetching the transaction
    print(f"\n   Fetching transaction {created_transaction['transaction_id']} via API...")
    response = requests.get(f"{API_BASE_URL}/api/transactions/{created_transaction['transaction_id']}")

    if response.status_code == 200:
        fetched = response.json()
        print(f"✅ Successfully fetched transaction")
        print(f"   - Retrieved Number: {fetched.get('transaction_number')}")
    else:
        print(f"❌ Failed to fetch transaction: {response.status_code}")

    return True

def print_ui_test_instructions():
    """Print instructions for manual UI testing."""
    print("\n" + "="*60)
    print("📱 MANUAL UI TESTING INSTRUCTIONS")
    print("="*60)
    print("\n1. Open your browser to: http://localhost:5173")
    print("\n2. Navigate to the Transactions page")
    print("\n3. Click 'Create Transaction' button")
    print("\n4. Fill in the form:")
    print("   - Transaction Type: Inbound")
    print("   - Product ID: 1")
    print("   - Warehouse ID: 1")
    print("   - Quantity Change: 100")
    print("   - Notes: Test transaction from UI")
    print("\n5. Click 'Create Transaction' button")
    print("\n6. Verify you see:")
    print("   ✅ Green success alert with transaction number")
    print("   ✅ Modal closes after 2 seconds")
    print("   ✅ Transaction appears in the list")
    print("\n7. Check the database to confirm the transaction was saved")

def main():
    """Run all tests."""
    print("="*60)
    print("🧪 END-TO-END TRANSACTION TEST")
    print("="*60)

    # Check services
    if not check_services():
        print("\n⚠️ Please start the services and try again")
        return 1

    # Run automated tests
    if not test_full_transaction_flow():
        print("\n❌ Automated tests failed")
        return 1

    # Print UI test instructions
    print_ui_test_instructions()

    print("\n" + "="*60)
    print("✅ AUTOMATED TESTS COMPLETED SUCCESSFULLY!")
    print("   Please perform the manual UI tests above.")
    print("="*60)
    return 0

if __name__ == "__main__":
    sys.exit(main())