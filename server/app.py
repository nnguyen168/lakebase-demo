"""FastAPI application for Databricks App Template."""

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from server.routers import router


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
  title='Databricks App API',
  description='Modern FastAPI application template for Databricks Apps with React frontend',
  version='0.1.0',
  lifespan=lifespan,
)

app.add_middleware(
  CORSMiddleware,
  allow_origins=['*'],  # Allow all origins in production since frontend and backend are on same domain
  allow_credentials=True,
  allow_methods=['*'],
  allow_headers=['*'],
)

app.include_router(router, prefix='/api', tags=['api'])


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


@app.get('/debug/env')
async def debug_env():
  """Debug endpoint to check environment variables."""
  return {
    'db_configured': bool(os.getenv('DB_HOST')),
    'db_host_present': bool(os.getenv('DB_HOST')),
    'db_user_present': bool(os.getenv('DB_USER')),
    'db_password_present': bool(os.getenv('DB_PASSWORD')),
    'db_name': os.getenv('DB_NAME', 'Not set'),
    'using_real_db': all([
      os.getenv('DB_HOST'),
      os.getenv('DB_USER'),
      os.getenv('DB_PASSWORD')
    ])
  }


# ============================================================================
# SERVE STATIC FILES FROM CLIENT BUILD DIRECTORY (MUST BE LAST!)
# ============================================================================
# This static file mount MUST be the last route registered!
# It catches all unmatched requests and serves the React app.
# Any routes added after this will be unreachable!
if os.path.exists('client/build'):
  app.mount('/', StaticFiles(directory='client/build', html=True), name='static')
