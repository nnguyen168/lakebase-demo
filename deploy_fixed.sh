#!/bin/bash

# Fixed deployment script for Databricks Apps
# This version properly uses uvx --from databricks-cli

set -e

# Parse command line arguments
VERBOSE=false
CREATE_APP=false
for arg in "$@"; do
  case $arg in
    --verbose)
      VERBOSE=true
      echo "🔍 Verbose mode enabled"
      ;;
    --create)
      CREATE_APP=true
      echo "🔧 App creation mode enabled"
      ;;
    *)
      echo "Unknown argument: $arg"
      echo "Usage: ./deploy_fixed.sh [--verbose] [--create]"
      exit 1
      ;;
  esac
done

# Load environment variables
if [ -f .env.local ]; then
  set -a
  source .env.local
  set +a
fi

# Validate required configuration
if [ -z "$DBA_SOURCE_CODE_PATH" ]; then
  echo "❌ DBA_SOURCE_CODE_PATH is not set. Please check .env.local"
  exit 1
fi

if [ -z "$DATABRICKS_APP_NAME" ]; then
  echo "❌ DATABRICKS_APP_NAME is not set. Please check .env.local"
  exit 1
fi

# Authentication
echo "🔐 Authenticating with Databricks..."
if [ "$DATABRICKS_AUTH_TYPE" = "pat" ]; then
  if [ -z "$DATABRICKS_HOST" ] || [ -z "$DATABRICKS_TOKEN" ]; then
    echo "❌ PAT authentication requires DATABRICKS_HOST and DATABRICKS_TOKEN"
    exit 1
  fi
  
  echo "Using Personal Access Token authentication"
  export DATABRICKS_HOST="$DATABRICKS_HOST"
  export DATABRICKS_TOKEN="$DATABRICKS_TOKEN"
  
  # Test connection
  if ! uvx --from databricks-cli databricks current-user me >/dev/null 2>&1; then
    echo "❌ PAT authentication failed. Please check your credentials."
    exit 1
  fi
else
  echo "❌ Only PAT authentication is supported in this script"
  exit 1
fi

echo "✅ Databricks authentication successful"

# Check if app needs to be created
if [ "$CREATE_APP" = true ]; then
  echo "🔍 Checking if app '$DATABRICKS_APP_NAME' exists..."
  
  APP_EXISTS=$(uvx --from databricks-cli databricks apps list 2>/dev/null | grep -c "^$DATABRICKS_APP_NAME " 2>/dev/null || echo "0")
  APP_EXISTS=$(echo "$APP_EXISTS" | head -1 | tr -d '\n')
  
  if [ "$APP_EXISTS" -eq 0 ]; then
    echo "❌ App '$DATABRICKS_APP_NAME' does not exist. Creating it..."
    echo "⏳ This may take several minutes..."
    
    if [ "$VERBOSE" = true ]; then
      uvx --from databricks-cli databricks apps create "$DATABRICKS_APP_NAME"
    else
      uvx --from databricks-cli databricks apps create "$DATABRICKS_APP_NAME" > /dev/null 2>&1
    fi
    
    echo "✅ App '$DATABRICKS_APP_NAME' created successfully"
  else
    echo "✅ App '$DATABRICKS_APP_NAME' already exists"
  fi
fi

mkdir -p build

# Generate requirements.txt
echo "📦 Generating requirements.txt..."
uv run python scripts/generate_semver_requirements.py

# Build frontend
echo "🏗️  Building frontend..."
cd client
if [ "$VERBOSE" = true ]; then
  npm run build
else
  npm run build > /dev/null 2>&1
fi
cd ..
echo "✅ Frontend build complete"

# Create workspace directory and upload source
echo "📂 Creating workspace directory..."
uvx --from databricks-cli databricks workspace mkdirs "$DBA_SOURCE_CODE_PATH"
echo "✅ Workspace directory created"

echo "📤 Syncing source code to workspace..."
uvx --from databricks-cli databricks sync . "$DBA_SOURCE_CODE_PATH"
echo "✅ Source code uploaded"

# Deploy to Databricks
echo "🚀 Deploying to Databricks..."
if [ "$VERBOSE" = true ]; then
  uvx --from databricks-cli databricks apps deploy "$DATABRICKS_APP_NAME" --source-code-path "$DBA_SOURCE_CODE_PATH" --debug
else
  uvx --from databricks-cli databricks apps deploy "$DATABRICKS_APP_NAME" --source-code-path "$DBA_SOURCE_CODE_PATH"
fi

echo ""
echo "✅ Deployment complete!"
echo ""

# Get the app URL
echo "🔍 Getting app URL..."
APP_URL=$(uvx --from databricks-cli databricks apps list --output json 2>/dev/null | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    if isinstance(data, list):
        apps = data
    else:
        apps = data.get('apps', [])
    for app in apps:
        if app.get('name') == '$DATABRICKS_APP_NAME':
            print(app.get('url', ''))
            break
except: pass
" 2>/dev/null)

if [ -n "$APP_URL" ]; then
  echo "Your app is available at:"
  echo "$APP_URL"
  echo ""
  echo "📊 Monitor deployment logs at (visit in browser):"
  echo "$APP_URL/logz"
else
  echo "Your app should be available at:"
  echo "$DATABRICKS_HOST/apps/$DATABRICKS_APP_NAME"
fi

echo ""
echo "To check the status:"
echo "uvx --from databricks-cli databricks apps list"
echo ""
echo "💡 If the app fails to start, visit the /logz endpoint in your browser for installation issues."