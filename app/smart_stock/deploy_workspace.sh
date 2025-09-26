#!/bin/bash

# Workspace deployment script - uploads code without creating an app
# Due to app limit, this prepares code for manual app creation or reuse

set -e

echo "🚀 Databricks Workspace Deployment (App Limit Workaround)"
echo "=========================================================="

# Load environment variables
if [ -f .env.local ]; then
  set -a
  source .env.local
  set +a
fi

# Validate configuration
if [ -z "$DBA_SOURCE_CODE_PATH" ] || [ -z "$DATABRICKS_HOST" ] || [ -z "$DATABRICKS_TOKEN" ]; then
  echo "❌ Missing required configuration in .env.local"
  exit 1
fi

export DATABRICKS_HOST="$DATABRICKS_HOST"
export DATABRICKS_TOKEN="$DATABRICKS_TOKEN"

# Test authentication
echo "🔐 Testing authentication..."
if ! uvx --from databricks-cli databricks current-user me >/dev/null 2>&1; then
  echo "❌ Authentication failed"
  exit 1
fi
echo "✅ Authentication successful"

# Generate requirements.txt
echo "📦 Generating requirements.txt..."
uv run python scripts/generate_semver_requirements.py

# Build frontend
echo "🏗️  Building frontend..."
cd client
npm run build > /dev/null 2>&1
cd ..
echo "✅ Frontend build complete"

# Create workspace directory
echo "📂 Creating workspace directory: $DBA_SOURCE_CODE_PATH"
uvx --from databricks-cli databricks workspace mkdirs "$DBA_SOURCE_CODE_PATH" 2>/dev/null || true

# Sync code to workspace
echo "📤 Syncing code to workspace..."
uvx --from databricks-cli databricks sync . "$DBA_SOURCE_CODE_PATH"
echo "✅ Code uploaded to workspace"

# Display next steps
echo ""
echo "=========================================================="
echo "✅ CODE DEPLOYMENT COMPLETE!"
echo "=========================================================="
echo ""
echo "Your code is now in the Databricks workspace at:"
echo "  $DBA_SOURCE_CODE_PATH"
echo ""
echo "⚠️  IMPORTANT: App creation limit reached (200 apps max)"
echo ""
echo "NEXT STEPS:"
echo "1. Ask your workspace admin to:"
echo "   - Delete unused apps to free up space, OR"
echo "   - Increase the app limit for the workspace"
echo ""
echo "2. Once space is available, create the app:"
echo "   uvx --from databricks-cli databricks apps create $DATABRICKS_APP_NAME"
echo ""
echo "3. Then deploy to the app:"
echo "   uvx --from databricks-cli databricks apps deploy $DATABRICKS_APP_NAME \\"
echo "     --source-code-path $DBA_SOURCE_CODE_PATH"
echo ""
echo "ALTERNATIVE: Reuse an existing app"
echo "1. Find an unused app:"
echo "   uvx --from databricks-cli databricks apps list"
echo ""
echo "2. Deploy to that app instead:"
echo "   uvx --from databricks-cli databricks apps deploy <existing-app-name> \\"
echo "     --source-code-path $DBA_SOURCE_CODE_PATH"
echo ""
echo "Your app.yaml is configured with Lakebase credentials ✅"
echo "The app will connect to your inventory database when deployed."