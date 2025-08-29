# 🔐 Persistent Database Authentication Guide

Your app currently uses OAuth tokens that expire every hour. Here's how to set up persistent authentication:

## Recommended Solution: Databricks Secrets

This is the most secure and maintainable approach for production.

### Step 1: Create a Secret Scope

```bash
uvx --from databricks-cli databricks secrets create-scope --scope lakebase-secrets
```

### Step 2: Store Your Database Password

```bash
# You'll be prompted to enter the password (paste your OAuth token)
uvx --from databricks-cli databricks secrets put --scope lakebase-secrets --key db-password
```

### Step 3: Update Your Code to Use Secrets

Create a new file `server/secrets_database.py`:

```python
import os
from databricks.sdk import WorkspaceClient
from databricks.sdk.runtime import dbutils

class SecretsLakebaseConnection:
    def __init__(self):
        # Get password from Databricks Secrets
        self.db_config = {
            "host": os.getenv("DB_HOST"),
            "port": int(os.getenv("DB_PORT", 5432)),
            "database": os.getenv("DB_NAME"),
            "user": os.getenv("DB_USER"),
            "password": dbutils.secrets.get(scope="lakebase-secrets", key="db-password"),
            "sslmode": "require",
        }
```

### Step 4: Update app.yaml

Remove the DB_PASSWORD environment variable since it will come from secrets:

```yaml
command: ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "8000"]
env:
  - name: DB_HOST
    value: "instance-1a754ee1-c83f-4de1-a321-684bd7230e59.database.cloud.databricks.com"
  - name: DB_PORT
    value: "5432"
  - name: DB_NAME
    value: "databricks_postgres"
  - name: DB_USER
    value: "nam.nguyen@databricks.com"
  # DB_PASSWORD will come from Databricks Secrets
```

### Step 5: Token Refresh Process

When the token expires (every hour), update the secret:

```bash
# Get new token from Databricks UI or API
# Then update the secret:
uvx --from databricks-cli databricks secrets put --scope lakebase-secrets --key db-password --string-value "NEW_TOKEN_HERE"

# The app will automatically use the new token without redeployment
```

## Alternative: Automated Token Refresh

Create a scheduled job that refreshes the token every 45 minutes:

```python
#!/usr/bin/env python3
import schedule
import time
import subprocess

def refresh_token():
    # 1. Get new token (this part needs to be automated based on your auth method)
    # 2. Update secret
    subprocess.run([
        "uvx", "--from", "databricks-cli", "databricks",
        "secrets", "put", "--scope", "lakebase-secrets",
        "--key", "db-password", "--string-value", new_token
    ])
    print(f"Token refreshed at {time.strftime('%Y-%m-%d %H:%M:%S')}")

# Schedule refresh every 45 minutes
schedule.every(45).minutes.do(refresh_token)

while True:
    schedule.run_pending()
    time.sleep(60)
```

## Quick Workaround: Manual Refresh

Until you implement secrets, you can manually refresh the token:

1. **Get new token** (every ~45 minutes to be safe):
   - Go to Databricks workspace
   - Navigate to SQL Warehouses or your cluster
   - Get the connection details/password

2. **Update app.yaml** with new token

3. **Redeploy** (takes ~30 seconds):
   ```bash
   source .env.local
   export DATABRICKS_HOST DATABRICKS_TOKEN
   uvx --from databricks-cli databricks sync . "$DBA_SOURCE_CODE_PATH"
   uvx --from databricks-cli databricks apps deploy nam-lakebase-inventory --source-code-path "$DBA_SOURCE_CODE_PATH"
   ```

## Long-term Solution: Request Service Principal

Contact your Databricks admin to:
1. Create a service principal for your app
2. Grant it access to Lakebase
3. Get non-expiring credentials

## Current Token Expiry

Your current token expires at approximately:
- **Created:** 19:39 UTC (iat: 1755200351)
- **Expires:** 20:39 UTC (exp: 1755203951)
- **Duration:** 1 hour

Set a reminder to refresh before expiry!

## Testing Connection

Test if your token is still valid:

```bash
source .env.local
uv run python -c "
import psycopg2
conn = psycopg2.connect(
    host='$DB_HOST',
    port=5432,
    database='$DB_NAME',
    user='$DB_USER',
    password='$DB_PASSWORD',
    sslmode='require'
)
print('✅ Token still valid!')
conn.close()
"
```

If it fails, you need to refresh the token.