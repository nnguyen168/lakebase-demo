#!/usr/bin/env python3
"""Refresh Lakebase OAuth token and update app configuration."""

import subprocess
import json
import os
from datetime import datetime

def get_fresh_token():
    """Get a fresh OAuth token from Databricks."""
    # This would need to be automated - for now, manual process
    print("=" * 60)
    print("TOKEN REFRESH INSTRUCTIONS")
    print("=" * 60)
    print()
    print("To get a fresh token that lasts longer:")
    print()
    print("1. Go to Databricks workspace")
    print("2. Open a SQL Warehouse or Compute cluster")
    print("3. Look for 'Connection Details' or 'JDBC/ODBC'")
    print("4. Find the password/token field")
    print("5. Copy the new token")
    print()
    print("Alternatively, use Databricks CLI:")
    print("uvx --from databricks-cli databricks auth token")
    print()
    return None

def update_app_yaml(new_token):
    """Update app.yaml with new token."""
    # Read current app.yaml
    with open('app.yaml', 'r') as f:
        lines = f.readlines()
    
    # Update the DB_PASSWORD line
    for i, line in enumerate(lines):
        if 'DB_PASSWORD' in line:
            # Update the next line which has the value
            if i + 1 < len(lines):
                lines[i + 1] = f'    value: "{new_token}"\n'
                break
    
    # Write back
    with open('app.yaml', 'w') as f:
        f.writelines(lines)
    
    print(f"✅ Updated app.yaml with new token")

def deploy_app():
    """Redeploy the app with updated token."""
    cmd = [
        "uvx", "--from", "databricks-cli", "databricks",
        "apps", "deploy", "nam-lakebase-inventory",
        "--source-code-path", os.getenv("DBA_SOURCE_CODE_PATH")
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ App redeployed successfully")
    else:
        print(f"❌ Deployment failed: {result.stderr}")

if __name__ == "__main__":
    print("Token Refresh Process")
    print("=" * 60)
    
    # For manual process
    token = input("Enter new OAuth token (or press Enter for instructions): ").strip()
    
    if not token:
        get_fresh_token()
    else:
        print(f"Token starts with: {token[:20]}...")
        
        # Update app.yaml
        update_app_yaml(token)
        
        # Sync and deploy
        print("Syncing to workspace...")
        subprocess.run([
            "uvx", "--from", "databricks-cli", "databricks",
            "sync", ".", os.getenv("DBA_SOURCE_CODE_PATH")
        ])
        
        print("Deploying app...")
        deploy_app()
        
        print("\n✅ Token refresh complete!")
        print(f"Token updated at: {datetime.now()}")