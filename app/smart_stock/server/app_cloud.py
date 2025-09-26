"""FastAPI application optimized for Databricks Apps cloud environment."""

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
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
  # Try to check database connection safely
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


# Serve the React app's index.html for the root route
@app.get('/')
async def serve_react_app():
  """Serve the React app index.html."""
  build_dir = Path('client/build')
  index_file = build_dir / 'index.html'
  
  if index_file.exists():
    return FileResponse(str(index_file), media_type='text/html')
  else:
    return {
      'message': 'Databricks App API is running!',
      'frontend': 'React app build not found',
      'build_dir_exists': build_dir.exists(),
      'available_endpoints': ['/health', '/debug/env', '/api', '/docs']
    }


# ============================================================================
# SERVE STATIC FILES (with error handling for cloud environment)
# ============================================================================
# Try to mount static files, but don't fail if it causes issues
try:
  if os.path.exists('client/build'):
    # Mount static assets
    if os.path.exists('client/build/assets'):
      app.mount('/assets', StaticFiles(directory='client/build/assets'), name='assets')
    
    # Serve favicon and other static files
    @app.get('/favicon.ico')
    async def favicon():
      favicon_path = Path('client/build/favicon.ico')
      if favicon_path.exists():
        return FileResponse(str(favicon_path))
      return {'error': 'favicon not found'}
      
except Exception as e:
  print(f"Warning: Could not mount static files: {e}")
  # Continue without static file serving