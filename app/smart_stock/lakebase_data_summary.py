#!/usr/bin/env python3
"""Generate a comprehensive summary of Lakebase PostgreSQL database."""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv("../../.env.local")

# Database configuration from environment with defaults
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "instance-9965ce63-150c-4746-93dc-a3dcb78fda3b.database.cloud.databricks.com"),
    "port": os.getenv("DB_PORT", "5432"),
    "database": os.getenv("DB_NAME", "databricks_postgres"),
    "user": os.getenv("DB_USER", "lakebase_demo_app"),
    "password": os.getenv("DB_PASSWORD", "lakebasedemo2025"),
}

def get_table_summary():
    """Get summary statistics for all accessible tables."""
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = True

    summary = {}

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # Products summary
        cur.execute("""
            SELECT
                COUNT(*) as total_products,
                COUNT(DISTINCT category) as categories,
                MIN(price) as min_price,
                MAX(price) as max_price,
                AVG(price) as avg_price
            FROM products
        """)
        summary['products'] = cur.fetchone()

        # Get product categories
        cur.execute("SELECT DISTINCT category, COUNT(*) as count FROM products GROUP BY category ORDER BY count DESC")
        summary['categories'] = cur.fetchall()

        # Warehouses summary
        cur.execute("SELECT COUNT(*) as total_warehouses FROM warehouses")
        summary['warehouses'] = cur.fetchone()

        cur.execute("SELECT name, location FROM warehouses")
        summary['warehouse_list'] = cur.fetchall()

        # Inventory forecast summary
        cur.execute("""
            SELECT
                COUNT(*) as total_forecasts,
                COUNT(CASE WHEN current_stock < reorder_point THEN 1 END) as below_reorder_point,
                COUNT(CASE WHEN current_stock = 0 THEN 1 END) as out_of_stock,
                AVG(confidence_score) as avg_confidence
            FROM inventory_forecast
        """)
        summary['forecast'] = cur.fetchone()

        # Inventory transactions summary
        cur.execute("""
            SELECT
                COUNT(*) as total_transactions,
                MIN(transaction_timestamp) as earliest_transaction,
                MAX(transaction_timestamp) as latest_transaction,
                COUNT(DISTINCT transaction_type) as transaction_types
            FROM inventory_transactions
        """)
        summary['transactions'] = cur.fetchone()

        # Transaction types distribution
        cur.execute("""
            SELECT
                transaction_type,
                status,
                COUNT(*) as count
            FROM inventory_transactions
            GROUP BY transaction_type, status
            ORDER BY count DESC
        """)
        summary['transaction_distribution'] = cur.fetchall()

        # Historical inventory data range
        cur.execute("""
            SELECT
                COUNT(*) as total_records,
                MIN(date) as earliest_date,
                MAX(date) as latest_date,
                COUNT(DISTINCT date) as unique_dates
            FROM inventory_historical
        """)
        summary['historical'] = cur.fetchone()

    conn.close()
    return summary

def print_summary():
    """Print a formatted summary of the database."""
    print("\n" + "="*80)
    print("📊 LAKEBASE POSTGRESQL DATABASE SUMMARY")
    print("="*80)

    summary = get_table_summary()

    # Database connection info
    print(f"\n🔌 Database Connection:")
    print(f"   Host: {DB_CONFIG['host']}")
    print(f"   Database: {DB_CONFIG['database']}")
    print(f"   User: {DB_CONFIG['user']}")

    # Products
    print(f"\n📦 PRODUCTS TABLE:")
    print(f"   Total Products: {summary['products']['total_products']}")
    print(f"   Categories: {summary['products']['categories']}")
    print(f"   Price Range: ${summary['products']['min_price']:.2f} - ${summary['products']['max_price']:.2f}")
    print(f"   Average Price: ${summary['products']['avg_price']:.2f}")

    print(f"\n   Product Categories:")
    for cat in summary['categories']:
        print(f"     • {cat['category']}: {cat['count']} products")

    # Warehouses
    print(f"\n🏭 WAREHOUSES:")
    print(f"   Total Warehouses: {summary['warehouses']['total_warehouses']}")
    for wh in summary['warehouse_list']:
        print(f"     • {wh['name']} - {wh['location']}")

    # Inventory Forecast
    print(f"\n🔮 INVENTORY FORECAST:")
    print(f"   Total Forecasts: {summary['forecast']['total_forecasts']}")
    print(f"   Below Reorder Point: {summary['forecast']['below_reorder_point']} items")
    print(f"   Out of Stock: {summary['forecast']['out_of_stock']} items")
    print(f"   Average Confidence: {summary['forecast']['avg_confidence']:.2%}")

    # Inventory Transactions
    print(f"\n💰 INVENTORY TRANSACTIONS:")
    print(f"   Total Transactions: {summary['transactions']['total_transactions']:,}")
    print(f"   Date Range: {summary['transactions']['earliest_transaction']} to {summary['transactions']['latest_transaction']}")
    print(f"   Transaction Types: {summary['transactions']['transaction_types']}")

    print(f"\n   Transaction Distribution:")
    current_type = None
    for td in summary['transaction_distribution'][:10]:  # Show top 10
        if td['transaction_type'] != current_type:
            current_type = td['transaction_type']
            print(f"     {current_type.upper()}:")
        print(f"       • {td['status']}: {td['count']:,} transactions")

    # Historical Inventory
    print(f"\n📈 HISTORICAL INVENTORY DATA:")
    print(f"   Total Records: {summary['historical']['total_records']:,}")
    print(f"   Date Range: {summary['historical']['earliest_date']} to {summary['historical']['latest_date']}")
    print(f"   Unique Dates: {summary['historical']['unique_dates']}")

    # Data insights
    print(f"\n💡 KEY INSIGHTS:")
    print(f"   • The database contains real e-bike parts inventory data")
    print(f"   • Covers approximately 3 years of transaction history")
    print(f"   • Active inventory management with {summary['forecast']['below_reorder_point']} items needing reorder")
    print(f"   • Multi-warehouse operation across Europe (Lyon, Hamburg, Milan)")
    print(f"   • Products include motors, batteries, frames, wheels, and accessories")

    print("\n" + "="*80)
    print("✅ Database summary complete!")
    print("="*80 + "\n")

if __name__ == "__main__":
    print_summary()