"""FastAPI application for Databricks App Template."""

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from server.routers import router
from server.routers import genie
from server.routers import agent
from server.routers import jobs


# Load environment variables from .env.local if it exists
def load_env_file(filepath: str) -> None:
  """Load environment variables from a file."""
  if Path(filepath).exists():
    with open(filepath) as f:
      for line in f:
        line = line.strip()
        if line and not line.startswith('#'):
          key, _, value = line.partition('=')
          if key and value:
            os.environ[key] = value


# Load .env files
load_env_file('.env')
load_env_file('.env.local')


@asynccontextmanager
async def lifespan(app: FastAPI):
  """Manage application lifespan."""
  yield


app = FastAPI(
  title='SmartStock API',
  description='Intelligent inventory management system for VulcanTech Manufacturing',
  version='1.0.0',
  lifespan=lifespan,
)

app.add_middleware(
  CORSMiddleware,
  allow_origins=['*'],  # Allow all origins in production since frontend and backend are on same domain
  allow_credentials=True,
  allow_methods=['*'],
  allow_headers=['*'],
)

# Add demo tracking for Databricks internal analytics
# Only tracks @databricks.com emails, data is anonymized at team level
try:
  from dbdemos_tracker import Tracker
  Tracker.add_tracker_fastapi(app, "smartstock", demo_catalog_id="10217")
except Exception as e:
  print(f"Demo tracker not available: {e}")

app.include_router(router, prefix='/api', tags=['api'])
app.include_router(genie.router)
app.include_router(agent.router)
app.include_router(jobs.router)


@app.get('/health')
async def health():
  """Health check endpoint."""
  # Try to check database connection
  try:
    from server.db_selector import db
    # Try a simple query
    result = db.execute_query("SELECT 1 as test", None)
    db_status = 'connected'
    db_type = 'postgres' if 'LakebasePostgres' in str(type(db)) else 'mock'
  except Exception as e:
    db_status = f'error: {str(e)}'
    db_type = 'unknown'
  
  return {
    'status': 'healthy',
    'database': db_status,
    'db_type': db_type
  }


@app.get('/api/config')
async def get_config():
  """Get frontend configuration from environment variables."""
  return {
    'dashboardEmbedUrl': os.environ.get('DASHBOARD_EMBED_URL', ''),
    'databricksHost': os.environ.get('DATABRICKS_HOST', ''),
    'resetDemoJobUrl': os.environ.get('RESET_DEMO_JOB_URL', ''),
  }


@app.get('/debug/env')
async def debug_env():
  """Debug endpoint to check environment variables."""
  app_resource = bool(os.getenv('PGHOST') and os.getenv('PGUSER'))
  legacy = all([os.getenv('DB_HOST'), os.getenv('DB_USER'), os.getenv('DB_PASSWORD')])
  return {
    'db_app_resource_mode': app_resource,
    'db_configured': app_resource or legacy,
    'pg_host': (os.getenv('PGHOST') or 'Not set')[:50],
    'pg_user': os.getenv('PGUSER', 'Not set'),
    'db_host': (os.getenv('DB_HOST') or 'Not set')[:50],
    'db_user': os.getenv('DB_USER', 'Not set'),
    'oauth_client_configured': bool(
      os.getenv('DATABRICKS_CLIENT_ID') and os.getenv('DATABRICKS_CLIENT_SECRET')
    ),
    'db_password_present': bool(os.getenv('DB_PASSWORD')),
    'db_name': os.getenv('PGDATABASE') or os.getenv('DB_NAME', 'Not set'),
    'db_port': os.getenv('PGPORT') or os.getenv('DB_PORT', 'Not set'),
    'using_real_db': app_resource or legacy,
  }

@app.get('/test-api')
async def test_api():
  """Serve test page for API debugging."""
  from fastapi.responses import HTMLResponse
  with open('test_frontend_api.html', 'r') as f:
    content = f.read()
  return HTMLResponse(content=content)

@app.get('/debug/db-test')
async def debug_db_test():
  """Test database connection and query."""
  import psycopg2
  from psycopg2.extras import RealDictCursor

  try:
    from server.postgres_database import lakebase_psycopg2_connect_kwargs

    db_config = lakebase_psycopg2_connect_kwargs()

    # Try to connect
    conn = psycopg2.connect(**db_config, cursor_factory=RealDictCursor)
    cursor = conn.cursor()

    # Count transactions
    schema = os.getenv('DB_SCHEMA', 'public')
    cursor.execute(f"SELECT COUNT(*) as count FROM {schema}.inventory_transactions")
    transaction_count = cursor.fetchone()['count']

    # Count products
    cursor.execute(f"SELECT COUNT(*) as count FROM {schema}.products")
    product_count = cursor.fetchone()['count']

    # Count warehouses
    cursor.execute(f"SELECT COUNT(*) as count FROM {schema}.warehouses")
    warehouse_count = cursor.fetchone()['count']

    cursor.close()
    conn.close()

    return {
      'connection': 'success',
      'transaction_count': transaction_count,
      'product_count': product_count,
      'warehouse_count': warehouse_count,
      'db_host': (db_config.get('host') or '')[:30] or 'None'
    }
  except Exception as e:
    return {
      'connection': 'failed',
      'error': str(e),
      'db_host': (os.getenv('PGHOST') or os.getenv('DB_HOST') or 'Not set')[:30],
      'db_user': os.getenv('PGUSER') or os.getenv('DB_USER', 'Not set')
    }


# ============================================================================
# SERVE STATIC FILES FROM CLIENT BUILD DIRECTORY (MUST BE LAST!)
# ============================================================================
# This static file mount MUST be the last route registered!
# It catches all unmatched requests and serves the React app.
# Any routes added after this will be unreachable!
# Check both possible build locations - production uses 'build', development uses 'client/build'
if os.path.exists('build'):
  app.mount('/', StaticFiles(directory='build', html=True), name='static')
elif os.path.exists('client/build'):
  app.mount('/', StaticFiles(directory='client/build', html=True), name='static')
