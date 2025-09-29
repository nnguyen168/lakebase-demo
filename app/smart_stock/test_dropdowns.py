#!/usr/bin/env python3
"""Test the dropdown endpoints and transaction creation with names."""

import requests
import json

API_BASE_URL = "http://localhost:8000"

def test_dropdowns():
    """Test fetching products and warehouses for dropdowns."""
    print("🧪 Testing Dropdown Endpoints")
    print("="*50)

    # Test fetching warehouses
    print("\n📦 Testing Warehouses Endpoint...")
    warehouses_response = requests.get(f"{API_BASE_URL}/api/warehouses/?limit=10")

    if warehouses_response.status_code == 200:
        data = warehouses_response.json()
        warehouses = data.get('items', [])
        print(f"✅ Fetched {len(warehouses)} warehouses:")
        for w in warehouses[:3]:
            print(f"   - ID: {w['warehouse_id']} | Name: {w['name']} | Location: {w['location']}")
    else:
        print(f"❌ Failed to fetch warehouses: {warehouses_response.status_code}")
        return False

    # Test fetching products
    print("\n📦 Testing Products Endpoint...")
    products_response = requests.get(f"{API_BASE_URL}/api/products/?limit=10")

    if products_response.status_code == 200:
        data = products_response.json()
        products = data.get('items', [])
        print(f"✅ Fetched {len(products)} products:")
        for p in products[:3]:
            print(f"   - ID: {p['product_id']} | Name: {p['name']} | SKU: {p['sku']}")
    else:
        print(f"❌ Failed to fetch products: {products_response.status_code}")
        return False

    # Test creating transaction with IDs from dropdowns
    if warehouses and products:
        print("\n🚀 Testing Transaction Creation with Dropdown Values...")

        selected_warehouse = warehouses[0]
        selected_product = products[0]

        print(f"\n   Selected:")
        print(f"   - Product: {selected_product['name']} (ID: {selected_product['product_id']})")
        print(f"   - Warehouse: {selected_warehouse['name']} (ID: {selected_warehouse['warehouse_id']})")

        transaction_data = {
            "product_id": selected_product['product_id'],
            "warehouse_id": selected_warehouse['warehouse_id'],
            "quantity_change": 25,
            "transaction_type": "inbound",
            "notes": f"Test with dropdown: {selected_product['name']} to {selected_warehouse['name']}"
        }

        response = requests.post(
            f"{API_BASE_URL}/api/transactions/",
            json=transaction_data,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            transaction = response.json()
            print(f"\n✅ Transaction created successfully!")
            print(f"   - Transaction Number: {transaction.get('transaction_number')}")
            print(f"   - Status: {transaction.get('status')}")
            print(f"   - Notes: {transaction.get('notes')}")
        else:
            print(f"❌ Failed to create transaction: {response.status_code}")
            print(f"   Error: {response.text}")
            return False

    print("\n" + "="*50)
    print("✅ ALL TESTS PASSED!")
    return True

if __name__ == "__main__":
    test_dropdowns()