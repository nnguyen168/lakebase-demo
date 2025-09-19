#!/usr/bin/env python3
"""Test the deployed Databricks app."""

import subprocess
import json

def test_app():
    """Test the deployed app status."""
    
    print("Testing Deployed App: nam-lakebase-inventory")
    print("=" * 50)
    
    # Get app details
    cmd = [
        "uvx", "--from", "databricks-cli", "databricks", 
        "apps", "get", "nam-lakebase-inventory", 
        "--output", "json"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        app_info = json.loads(result.stdout)
        
        print(f"App Status: {app_info.get('app_status', {}).get('state', 'Unknown')}")
        print(f"Compute Status: {app_info.get('compute_status', {}).get('state', 'Unknown')}")
        print(f"URL: {app_info.get('url', 'Not available')}")
        
        if app_info.get('active_deployment'):
            deployment = app_info['active_deployment']
            print(f"Deployment Status: {deployment.get('status', {}).get('state', 'Unknown')}")
            print(f"Last Updated: {deployment.get('update_time', 'Unknown')}")
        
        print("\n" + "=" * 50)
        print("DIAGNOSIS:")
        print("-" * 50)
        
        if app_info.get('app_status', {}).get('state') == 'RUNNING':
            print("✅ App is running successfully")
            print("\nThe 'Failed to fetch' error is likely due to:")
            print("1. OAuth authentication required - Access the app through your browser")
            print("2. The app needs to be accessed while logged into Databricks")
            print("\nTO ACCESS YOUR APP:")
            print(f"1. Go to: {app_info.get('url', 'Not available')}")
            print("2. You'll be redirected to Databricks login")
            print("3. After login, the app should load with your data")
            print("\nALTERNATIVE ACCESS:")
            print(f"1. Go to your Databricks workspace: https://e2-demo-field-eng.cloud.databricks.com/")
            print("2. Navigate to Apps section")
            print("3. Find 'nam-lakebase-inventory' and click to open")
        else:
            print("❌ App is not running properly")
            print("Check the logs at: <app-url>/logz")
    else:
        print(f"Error getting app details: {result.stderr}")

if __name__ == "__main__":
    test_app()