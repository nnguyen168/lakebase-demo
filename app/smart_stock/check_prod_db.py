#!/usr/bin/env python3
"""Check production database for products and warehouses."""

import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')

# Database connection parameters
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT', 5432)
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

def check_database():
    """Check database for products and warehouses."""
    try:
        # Connect to database
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cur = conn.cursor()

        # Check products
        cur.execute("SELECT COUNT(*) FROM products")
        product_count = cur.fetchone()[0]
        print(f"Products in database: {product_count}")

        if product_count == 0:
            print("No products found! Database needs to be populated.")
        else:
            cur.execute("SELECT product_id, name FROM products LIMIT 5")
            print("Sample products:")
            for row in cur.fetchall():
                print(f"  - {row[0]}: {row[1]}")

        # Check warehouses
        cur.execute("SELECT COUNT(*) FROM warehouses")
        warehouse_count = cur.fetchone()[0]
        print(f"\nWarehouses in database: {warehouse_count}")

        if warehouse_count == 0:
            print("No warehouses found! Database needs to be populated.")
        else:
            cur.execute("SELECT warehouse_id, name FROM warehouses")
            print("Warehouses:")
            for row in cur.fetchall():
                print(f"  - {row[0]}: {row[1]}")

        # Check transactions
        cur.execute("SELECT COUNT(*) FROM inventory_transactions")
        transaction_count = cur.fetchone()[0]
        print(f"\nTransactions in database: {transaction_count}")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"Error connecting to database: {e}")
        return False

    return True

if __name__ == "__main__":
    check_database()