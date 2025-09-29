#!/usr/bin/env python3
"""Test the deployed Databricks App API endpoints."""

import requests
import json
import time

APP_URL = "https://smart-stock-3813697403783275.aws.databricksapps.com"

def test_deployed_app():
    """Test the deployed app endpoints."""
    print("🧪 Testing Deployed Databricks App")
    print("="*50)
    print(f"App URL: {APP_URL}")

    # Test health endpoint
    print("\n📊 Testing Health Check...")
    try:
        response = requests.get(f"{APP_URL}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health check passed")
        else:
            print(f"⚠️ Health check returned: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Health check failed: {e}")

    # Test API docs
    print("\n📚 Testing API Documentation...")
    try:
        response = requests.get(f"{APP_URL}/docs", timeout=10)
        if response.status_code == 200:
            print("✅ API documentation is accessible")
        else:
            print(f"⚠️ API docs returned: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"⚠️ API docs failed: {e}")

    # Test warehouses endpoint
    print("\n🏭 Testing Warehouses Endpoint...")
    try:
        response = requests.get(f"{APP_URL}/api/warehouses/?limit=2", timeout=10)
        if response.status_code == 200:
            data = response.json()
            warehouses = data.get('items', [])
            print(f"✅ Fetched {len(warehouses)} warehouses")
            if warehouses:
                print(f"   First warehouse: {warehouses[0].get('name')}")
        else:
            print(f"❌ Warehouses endpoint returned: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Warehouses endpoint failed: {e}")

    # Test products endpoint
    print("\n📦 Testing Products Endpoint...")
    try:
        response = requests.get(f"{APP_URL}/api/products/?limit=2", timeout=10)
        if response.status_code == 200:
            data = response.json()
            products = data.get('items', [])
            print(f"✅ Fetched {len(products)} products")
            if products:
                print(f"   First product: {products[0].get('name')}")
        else:
            print(f"❌ Products endpoint returned: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Products endpoint failed: {e}")

    # Test transactions endpoint
    print("\n💼 Testing Transactions Endpoint...")
    try:
        response = requests.get(f"{APP_URL}/api/transactions/?limit=2", timeout=10)
        if response.status_code == 200:
            data = response.json()
            transactions = data.get('items', [])
            print(f"✅ Fetched {len(transactions)} transactions")
            if transactions:
                print(f"   Latest transaction: {transactions[0].get('transaction_number')}")
        else:
            print(f"❌ Transactions endpoint returned: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Transactions endpoint failed: {e}")

    print("\n" + "="*50)
    print("📱 Frontend URL: " + APP_URL)
    print("📚 API Docs URL: " + APP_URL + "/docs")
    print("📊 Logs URL: " + APP_URL + "/logz (requires browser authentication)")
    print("="*50)

if __name__ == "__main__":
    test_deployed_app()