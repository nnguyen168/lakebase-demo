"""FastAPI application with progressive feature loading for Databricks Apps."""

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

# Load environment variables
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
  allow_origins=['*'],
  allow_credentials=True,
  allow_methods=['*'],
  allow_headers=['*'],
)


@app.get('/health')
async def health():
  """Health check endpoint."""
  return {
    'status': 'healthy',
    'message': 'App is running successfully',
    'environment': 'databricks_apps'
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
    'build_dir_exists': Path('client/build').exists()
  }


# Try to add API routes safely
try:
  from server.routers import router
  app.include_router(router, prefix='/api', tags=['api'])
  print("✅ API routes loaded successfully")
except Exception as e:
  print(f"⚠️  Could not load API routes: {e}")
  
  # Add a fallback API route
  @app.get('/api/status')
  async def api_status():
    return {'status': 'API routes not available', 'error': str(e)}


# Serve React app
@app.get('/')
async def serve_react_app():
  """Serve the React app."""
  build_dir = Path('client/build')
  index_file = build_dir / 'index.html'
  
  if index_file.exists():
    return FileResponse(str(index_file), media_type='text/html')
  else:
    return {
      'message': 'Databricks App is running!',
      'frontend_status': 'React build not available',
      'available_endpoints': ['/health', '/debug/env', '/api', '/docs'],
      'build_dir_exists': build_dir.exists()
    }


# Basic static file serving for assets
@app.get('/assets/{file_path:path}')
async def serve_assets(file_path: str):
  """Serve static assets."""
  asset_path = Path(f'client/build/assets/{file_path}')
  if asset_path.exists() and asset_path.is_file():
    return FileResponse(str(asset_path))
  return {'error': 'Asset not found', 'path': file_path}