# Lakebase Connection Troubleshooting

## Current Connection Issue

The application is attempting to connect to Lakebase with these credentials:
- **Host**: instance-bb9eb530-d714-40f1-be9f-900b0c17af89.database.azuredatabricks.net
- **Port**: 5432
- **Database**: databricks_postgres
- **User**: nam.nguyen@databricks.com
- **Password**: Personal Access Token (dapidda...)

## Error Encountered
```
FATAL: password authentication failed for user "nam.nguyen@databricks.com"
```

## Possible Solutions

### 1. Verify Authentication Method
The password appears to be a JWT token. Lakebase might require:
- Token-based authentication instead of password
- A different connection string format
- OAuth2 authentication flow

### 2. Check Database Access
Verify in Databricks UI:
1. Go to your Databricks workspace
2. Navigate to Data → Lakebase (or SQL → Databases)
3. Check if `databricks_postgres` database exists
4. Verify user permissions for `nam.nguyen@databricks.com`

### 3. Alternative Connection Methods

#### Option A: Use Databricks CLI to get fresh token
```bash
databricks auth token --host https://adb-2338896885246877.17.azuredatabricks.net/
```

#### Option B: Use Personal Access Token
1. Go to Databricks workspace → User Settings → Access Tokens
2. Generate a new Personal Access Token
3. Use this token as the password

#### Option C: Use Service Principal
If using a service principal, the connection might need:
```python
"user": "service-principal-client-id",
"password": "service-principal-secret"
```

### 4. Test Connection with psql
Try connecting directly with psql to verify credentials:
```bash
psql "host=instance-bb9eb530-d714-40f1-be9f-900b0c17af89.database.azuredatabricks.net \
      port=5432 \
      dbname=databricks_postgres \
      user=nam.nguyen@databricks.com \
      sslmode=require"
```

## Current Workaround

The application is configured to automatically fall back to mock database when Lakebase connection fails. This allows development to continue while connection issues are resolved.

To switch between databases:
- **Mock Database**: Remove or rename `.env.local` 
- **Lakebase**: Ensure correct credentials in `.env.local`

## Next Steps

1. **Verify the authentication method** required by your Lakebase instance
2. **Check with Databricks documentation** for Lakebase connection requirements
3. **Contact Databricks support** if authentication continues to fail

## Application Status

✅ **Frontend**: Running successfully at http://localhost:5173
✅ **Backend**: Running with mock database at http://localhost:8000
⚠️ **Lakebase**: Connection pending (authentication issue)

The application will automatically switch to Lakebase once valid credentials are provided in `.env.local`.