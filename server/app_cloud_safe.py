"""FastAPI application optimized for Databricks Apps with safe API loading."""

import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query
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


# Initialize database connection safely
db = None
try:
    from server.db_selector import db
    db_available = True
    print("✅ Database connection initialized")
except Exception as e:
    db_available = False
    print(f"⚠️  Database not available: {e}")


@app.get('/health')
async def health():
    """Health check endpoint."""
    db_status = 'disconnected'
    db_type = 'none'
    
    if db_available and db:
        try:
            result = db.execute_query("SELECT 1 as test", None)
            db_status = 'connected'
            db_type = 'postgres' if 'LakebasePostgres' in str(type(db)) else 'mock'
        except Exception as e:
            db_status = f'error: {str(e)}'
    
    return {
        'status': 'healthy',
        'database': db_status,
        'db_type': db_type,
        'db_available': db_available
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
        'build_dir_exists': Path('client/build').exists(),
        'db_available': db_available
    }


# ============================================================================
# SAFE API ROUTES - Direct implementations to avoid import issues
# ============================================================================

@app.get('/api/user/me')
async def get_current_user():
    """Get current user info from Databricks context."""
    try:
        from databricks.sdk import WorkspaceClient
        w = WorkspaceClient()
        user = w.current_user.me()
        return {
            'userName': user.user_name or 'unknown',
            'displayName': user.display_name or 'Unknown User', 
            'active': user.active,
            'emails': [email.value for email in (user.emails or [])]
        }
    except Exception as e:
        return {
            'userName': 'demo_user@databricks.com',
            'displayName': 'Demo User',
            'active': True,
            'emails': ['demo_user@databricks.com']
        }


# Mock data for when database is not available
MOCK_ORDERS = [
    {
        "order_id": 1,
        "order_number": "ORD-2024-001",
        "product": "Widget A",
        "quantity": 100,
        "store": "Store 001",
        "requested_by": "John Doe",
        "order_date": "2024-01-15",
        "status": "pending"
    },
    {
        "order_id": 2,
        "order_number": "ORD-2024-002",
        "product": "Widget B",
        "quantity": 50,
        "store": "Store 002", 
        "requested_by": "Jane Smith",
        "order_date": "2024-01-14",
        "status": "approved"
    }
]

MOCK_INVENTORY = [
    {
        "item_id": "WID-A-001",
        "item_name": "Widget A",
        "stock": 500,
        "forecast_30_days": 200,
        "status": "in_stock",
        "action": "No Action"
    },
    {
        "item_id": "WID-B-002", 
        "item_name": "Widget B",
        "stock": 25,
        "forecast_30_days": 100,
        "status": "low_stock",
        "action": "Reorder Now"
    }
]


@app.get('/api/orders/')
async def get_orders():
    """Get orders list."""
    if db_available and db:
        try:
            result = db.execute_query("""
                SELECT 
                    o.order_id,
                    o.order_number,
                    p.name as product,
                    o.quantity,
                    o.store_id as store,
                    o.requested_by,
                    o.order_date,
                    o.status
                FROM orders o
                JOIN products p ON o.product_id = p.product_id
                ORDER BY o.order_date DESC LIMIT 50
            """, None)
            return result
        except Exception:
            pass
    
    return MOCK_ORDERS


@app.get('/api/orders/kpi')
async def get_order_kpis():
    """Get order management KPIs."""
    return {
        "total_orders": 156,
        "pending_orders": 12,
        "approved_orders": 89,
        "shipped_orders": 55,
        "average_order_value": 1250.75
    }


@app.get('/api/inventory/forecast')
async def get_inventory_forecast():
    """Get inventory forecast."""
    if db_available and db:
        try:
            result = db.execute_query("""
                SELECT 
                    p.sku as item_id,
                    p.name as item_name,
                    f.current_stock as stock,
                    f.forecast_30_days,
                    f.status,
                    CASE 
                        WHEN f.status = 'out_of_stock' THEN 'Urgent Reorder'
                        WHEN f.status = 'reorder_needed' THEN 'Reorder Now'
                        WHEN f.status = 'low_stock' THEN 'Monitor'
                        ELSE 'No Action'
                    END as action
                FROM inventory_forecast f
                JOIN products p ON f.product_id = p.product_id
                ORDER BY f.last_updated DESC LIMIT 50
            """, None)
            return result
        except Exception:
            pass
    
    return MOCK_INVENTORY


@app.get('/api/inventory/alerts/kpi')
async def get_inventory_alert_kpis():
    """Get inventory alert KPIs."""
    return {
        "low_stock_items": 8,
        "out_of_stock_items": 2,
        "reorder_needed_items": 5,
        "total_alerts": 15
    }


# ============================================================================
# REACT APP SERVING
# ============================================================================

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
            'status': 'React build not found',
            'available_endpoints': ['/health', '/debug/env', '/api/orders/', '/api/inventory/forecast', '/docs']
        }


# Static asset serving
@app.get('/assets/{file_path:path}')
async def serve_assets(file_path: str):
    """Serve static assets."""
    asset_path = Path(f'client/build/assets/{file_path}')
    if asset_path.exists() and asset_path.is_file():
        # Determine content type
        if file_path.endswith('.js'):
            media_type = 'application/javascript'
        elif file_path.endswith('.css'):
            media_type = 'text/css'
        else:
            media_type = 'application/octet-stream'
        
        return FileResponse(str(asset_path), media_type=media_type)
    
    return {'error': 'Asset not found', 'path': file_path}


@app.get('/favicon.ico')
async def serve_favicon():
    """Serve favicon."""
    favicon_path = Path('client/build/favicon.ico')
    if favicon_path.exists():
        return FileResponse(str(favicon_path))
    return {'error': 'favicon not found'}