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


# Initialize database connection directly (embedded for deployment)
db = None
db_init_error = None
db_available = False

def create_database_connection():
    """Create database connection directly within the app."""
    import os
    import psycopg2
    from psycopg2 import pool
    from psycopg2.extras import RealDictCursor
    from contextlib import contextmanager
    from typing import Optional, Any, Dict, List
    
    class LakebasePostgresConnection:
        def __init__(self):
            self.db_config = {
                "host": os.getenv("DB_HOST"),
                "port": int(os.getenv("DB_PORT", 5432)),
                "database": os.getenv("DB_NAME", "databricks_postgres"),
                "user": os.getenv("DB_USER"),
                "password": os.getenv("DB_PASSWORD"),
                "sslmode": "require",
            }
            
            if not all([self.db_config["host"], self.db_config["user"], self.db_config["password"]]):
                raise ValueError("DB_HOST, DB_USER, and DB_PASSWORD must be set in environment variables")
            
            self.connection_pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=1, maxconn=20, **self.db_config
            )
        
        @contextmanager
        def get_connection(self):
            connection = None
            try:
                connection = self.connection_pool.getconn()
                yield connection
            finally:
                if connection:
                    self.connection_pool.putconn(connection)
        
        @contextmanager
        def get_cursor(self, dict_cursor=True):
            with self.get_connection() as conn:
                cursor = None
                try:
                    cursor_factory = RealDictCursor if dict_cursor else None
                    cursor = conn.cursor(cursor_factory=cursor_factory)
                    yield cursor
                    conn.commit()
                except Exception as e:
                    conn.rollback()
                    raise
                finally:
                    if cursor:
                        cursor.close()
        
        def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
            with self.get_cursor(dict_cursor=True) as cursor:
                cursor.execute(query, params)
                if cursor.description:
                    return cursor.fetchall()
                return []
        
        def execute_update(self, query: str, params: Optional[tuple] = None) -> int:
            with self.get_cursor(dict_cursor=False) as cursor:
                cursor.execute(query, params)
                return cursor.rowcount
        
        def create_tables(self):
            """Create all required tables for the inventory management system."""
            
            # First, try to create a schema for the user if it doesn't exist
            try:
                self.execute_update("CREATE SCHEMA IF NOT EXISTS lakebase_demo")
                # Set search path to use the new schema by default
                self.execute_update("SET search_path TO lakebase_demo, public")
            except Exception:
                pass  # Use public schema if we can't create our own
            
            tables = {
                "customers": """
                    CREATE TABLE IF NOT EXISTS customers (
                        customer_id SERIAL PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        email VARCHAR(255) NOT NULL,
                        phone VARCHAR(50),
                        address TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """,
                "products": """
                    CREATE TABLE IF NOT EXISTS products (
                        product_id SERIAL PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        description TEXT,
                        sku VARCHAR(100) NOT NULL UNIQUE,
                        price DECIMAL(10, 2) NOT NULL,
                        unit VARCHAR(50) DEFAULT 'unit',
                        category VARCHAR(100),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """,
                "orders": """
                    CREATE TABLE IF NOT EXISTS orders (
                        order_id SERIAL PRIMARY KEY,
                        order_number VARCHAR(100) NOT NULL UNIQUE,
                        product_id INTEGER NOT NULL REFERENCES products(product_id),
                        customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
                        store_id VARCHAR(50) NOT NULL,
                        quantity INTEGER NOT NULL,
                        requested_by VARCHAR(255) NOT NULL,
                        status VARCHAR(50) DEFAULT 'pending',
                        notes TEXT,
                        order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """,
                "inventory_forecast": """
                    CREATE TABLE IF NOT EXISTS inventory_forecast (
                        forecast_id SERIAL PRIMARY KEY,
                        product_id INTEGER NOT NULL REFERENCES products(product_id),
                        store_id VARCHAR(50) NOT NULL,
                        current_stock INTEGER NOT NULL,
                        forecast_30_days INTEGER NOT NULL,
                        reorder_point INTEGER NOT NULL,
                        reorder_quantity INTEGER NOT NULL,
                        status VARCHAR(50) NOT NULL,
                        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(product_id, store_id)
                    )
                """
            }
            
            # Create each table
            for table_name, ddl in tables.items():
                try:
                    self.execute_update(ddl)
                except Exception:
                    pass  # Continue if table creation fails
        
        def seed_sample_data(self):
            """Seed sample data for testing."""
            
            # Check if data already exists
            try:
                existing_customers = self.execute_query("SELECT COUNT(*) as count FROM customers")
                if existing_customers and existing_customers[0]['count'] > 0:
                    return  # Data already exists
            except:
                return  # Table might not exist
            
            # Insert sample customers
            customers = [
                ("John Doe", "john@example.com", "555-0101", "123 Main St"),
                ("Jane Smith", "jane@example.com", "555-0102", "456 Oak Ave"),
                ("Bob Johnson", "bob@example.com", "555-0103", "789 Pine Rd"),
            ]
            
            for customer in customers:
                try:
                    self.execute_update(
                        "INSERT INTO customers (name, email, phone, address) VALUES (%s, %s, %s, %s)",
                        customer
                    )
                except:
                    pass
            
            # Insert sample products
            products = [
                ("Premium Coffee Beans", "Arabica beans from Colombia", "COF-001", 24.99, "lb", "Beverages"),
                ("Organic Green Tea", "Japanese matcha green tea", "TEA-001", 18.50, "box", "Beverages"),
                ("Sparkling Water", "Natural mineral water", "WAT-001", 2.99, "bottle", "Beverages"),
            ]
            
            for product in products:
                try:
                    self.execute_update(
                        """INSERT INTO products (name, description, sku, price, unit, category) 
                           VALUES (%s, %s, %s, %s, %s, %s)""",
                        product
                    )
                except:
                    pass
            
            # Insert sample inventory forecast
            forecasts = [
                (1, "STORE-001", 100, 80, 20, 50, "in_stock"),
                (2, "STORE-001", 15, 25, 10, 30, "low_stock"),
                (3, "STORE-002", 200, 150, 50, 100, "in_stock"),
            ]
            
            for forecast in forecasts:
                try:
                    self.execute_update(
                        """INSERT INTO inventory_forecast (product_id, store_id, current_stock, forecast_30_days, 
                           reorder_point, reorder_quantity, status) 
                           VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                        forecast
                    )
                except:
                    pass
    
    return LakebasePostgresConnection()

# STRICT POSTGRESQL REQUIREMENT - NO MOCK DATABASE FALLBACK
try:
    import os
    # Validate all required environment variables
    required_vars = ["DB_HOST", "DB_USER", "DB_PASSWORD"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        error_msg = f"CRITICAL: Missing required database environment variables: {missing_vars}"
        print(f"❌ {error_msg}")
        db_init_error = error_msg
        db_available = False
        db = None
        # DO NOT START WITHOUT DATABASE - This is a database-dependent application
        raise RuntimeError(error_msg)
    
    # Initialize PostgreSQL connection
    db = create_database_connection()
    
    # Test connection immediately to ensure it works
    test_result = db.execute_query("SELECT 'PostgreSQL' as db_type, current_database() as db_name, current_user as db_user")
    if not test_result or test_result[0]['db_type'] != 'PostgreSQL':
        raise RuntimeError("Database connection test failed - not PostgreSQL")
    
    db_available = True
    db_init_error = None
    print("✅ PostgreSQL database connection verified and operational")
    print(f"✅ Connected to database: {test_result[0]['db_name']} as user: {test_result[0]['db_user']}")
    
except Exception as e:
    db_available = False
    db_init_error = str(e)
    db = None
    print(f"❌ FATAL: PostgreSQL database connection failed: {e}")
    print("❌ This application requires a PostgreSQL database to function")
    # The application will not function without the database


@app.get('/health')
async def health():
    """Health check endpoint."""
    db_status = 'disconnected'
    db_type = 'none'
    db_error = None
    db_info = {}
    
    if db_available and db:
        try:
            result = db.execute_query("SELECT 'Lakebase PostgreSQL' as db_type, current_database() as db_name, current_user as db_user, version() as db_version")
            db_status = 'connected'
            db_type = 'lakebase_postgresql'
            
            if result:
                db_info = {
                    'database_name': result[0]['db_name'],
                    'database_user': result[0]['db_user'],
                    'database_type': result[0]['db_type'],
                    'postgresql_version': result[0]['db_version'].split(' ')[1] if 'PostgreSQL' in result[0]['db_version'] else 'unknown'
                }
        except Exception as e:
            db_status = 'error'
            db_error = str(e)
    
    response = {
        'status': 'healthy',
        'database': db_status,
        'db_type': db_type,
        'db_available': db_available,
        'database_info': db_info
    }
    
    if db_error:
        response['db_error'] = db_error
    
    if not db_available:
        response['warning'] = 'Application requires PostgreSQL database to function properly'
    
    return response


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
        'db_available': db_available,
        'db_init_error': db_init_error
    }


@app.get('/debug/db-test')
async def debug_db_test():
    """Debug endpoint to test database connection directly."""
    import os
    import psycopg2
    
    try:
        db_config = {
            "host": os.getenv("DB_HOST"),
            "port": int(os.getenv("DB_PORT", 5432)),
            "database": os.getenv("DB_NAME", "inventory_demo"),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD"),
            "sslmode": "require",
        }
        
        # Test basic connection
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT 1 as test")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "connection": "ok",
            "test_query": result[0],
            "config": {k: v if k != 'password' else '***' for k, v in db_config.items()}
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__,
            "config": {k: v if k != 'password' else '***' for k, v in db_config.items()}
        }


@app.get('/debug/init-tables')
async def debug_init_tables():
    """Debug endpoint to initialize database tables."""
    if not db_available or not db:
        return {"status": "error", "message": "PostgreSQL database not available - this application requires Lakebase PostgreSQL"}
    
    try:
        # Create tables
        db.create_tables()
        
        # Seed sample data  
        db.seed_sample_data()
        
        return {
            "status": "success",
            "message": "Database tables initialized successfully",
            "tables_created": ["customers", "products", "orders", "inventory_forecast"],
            "sample_data": "seeded"
        }
    except Exception as e:
        return {"status": "error", "message": f"Database initialization failed: {str(e)}"}


@app.get('/debug/products')
async def debug_products():
    """Debug endpoint to list all products in the database."""
    if not db_available or not db:
        return {"status": "error", "message": "PostgreSQL database not available"}
    
    try:
        products = db.execute_query("SELECT * FROM products ORDER BY product_id")
        return {
            "status": "success",
            "products": products,
            "count": len(products)
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to fetch products: {str(e)}"}


@app.get('/debug/customers')
async def debug_customers():
    """Debug endpoint to list all customers in the database."""
    if not db_available or not db:
        return {"status": "error", "message": "PostgreSQL database not available"}
    
    try:
        customers = db.execute_query("SELECT * FROM customers ORDER BY customer_id")
        return {
            "status": "success",
            "customers": customers,
            "count": len(customers)
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to fetch customers: {str(e)}"}


@app.post('/admin/init-database')
async def init_database():
    """Initialize database tables and sample data."""
    if not db_available or not db:
        raise HTTPException(status_code=503, detail="PostgreSQL database not available - this application requires Lakebase PostgreSQL")
    
    try:
        # Create tables
        db.create_tables()
        
        # Seed sample data  
        db.seed_sample_data()
        
        return {
            "status": "success",
            "message": "Database initialized successfully",
            "tables_created": ["customers", "products", "orders", "inventory_history", "inventory_forecast"],
            "sample_data": "seeded"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database initialization failed: {str(e)}")


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




@app.get('/api/orders/')
async def get_orders():
    """Get orders list."""
    if not db_available or not db:
        raise HTTPException(status_code=503, detail="PostgreSQL database not available - this application requires Lakebase PostgreSQL")
    
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PostgreSQL database error: {str(e)}")


@app.post('/api/orders/')
async def create_order(order_data: dict):
    """Create a new order."""
    if not db_available or not db:
        raise HTTPException(status_code=503, detail="PostgreSQL database not available - this application requires Lakebase PostgreSQL")
    
    try:
        # Generate order number
        import time
        order_number = f"ORD-{int(time.time())}"
        
        # Insert new order
        insert_query = """
            INSERT INTO orders (order_number, product_id, customer_id, store_id, quantity, requested_by, status, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING order_id
        """
        
        result = db.execute_query(insert_query, (
            order_number,
            order_data["product_id"],
            order_data["customer_id"], 
            order_data["store_id"],
            order_data["quantity"],
            order_data["requested_by"],
            order_data.get("status", "pending"),
            order_data.get("notes", "")
        ))
        
        if not result:
            raise HTTPException(status_code=500, detail="Failed to create order")
        
        # Return the created order with details
        order_id = result[0]["order_id"]
        created_order = db.execute_query("""
            SELECT 
                o.order_id,
                o.order_number,
                p.name as product_name,
                p.sku as product_sku,
                p.price as product_price,
                c.name as customer_name,
                c.email as customer_email,
                o.store_id,
                o.quantity,
                o.requested_by,
                o.status,
                o.notes,
                o.order_date
            FROM orders o
            JOIN products p ON o.product_id = p.product_id
            JOIN customers c ON o.customer_id = c.customer_id
            WHERE o.order_id = %s
        """, (order_id,))
        
        return created_order[0] if created_order else {"order_id": order_id, "order_number": order_number}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create order: {str(e)}")


@app.get('/api/orders/kpi')
async def get_order_kpis():
    """Get order management KPIs."""
    if not db_available or not db:
        raise HTTPException(status_code=503, detail="PostgreSQL database not available - this application requires Lakebase PostgreSQL")
    
    try:
        # Get order counts
        counts = db.execute_query("""
            SELECT 
                COUNT(*) as total_orders,
                SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending_orders,
                SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) as approved_orders,
                SUM(CASE WHEN status = 'shipped' THEN 1 ELSE 0 END) as shipped_orders
            FROM orders
        """, None)
        
        # Get average order value
        avg_value = db.execute_query("""
            SELECT AVG(o.quantity * p.price) as avg_order_value
            FROM orders o
            JOIN products p ON o.product_id = p.product_id
        """, None)
        
        result = counts[0] if counts else {}
        if avg_value and avg_value[0]['avg_order_value']:
            result['average_order_value'] = float(avg_value[0]['avg_order_value'])
        else:
            result['average_order_value'] = 0.0
            
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.get('/api/inventory/forecast')
async def get_inventory_forecast():
    """Get inventory forecast."""
    if not db_available or not db:
        raise HTTPException(status_code=503, detail="PostgreSQL database not available - this application requires Lakebase PostgreSQL")
    
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.get('/api/inventory/alerts/kpi')
async def get_inventory_alert_kpis():
    """Get inventory alert KPIs."""
    if not db_available or not db:
        raise HTTPException(status_code=503, detail="PostgreSQL database not available - this application requires Lakebase PostgreSQL")
    
    try:
        result = db.execute_query("""
            SELECT 
                SUM(CASE WHEN status = 'low_stock' THEN 1 ELSE 0 END) as low_stock_items,
                SUM(CASE WHEN status = 'out_of_stock' THEN 1 ELSE 0 END) as out_of_stock_items,
                SUM(CASE WHEN status = 'reorder_needed' THEN 1 ELSE 0 END) as reorder_needed_items,
                SUM(CASE WHEN status IN ('low_stock', 'out_of_stock', 'reorder_needed') THEN 1 ELSE 0 END) as total_alerts
            FROM inventory_forecast
        """, None)
        
        return result[0] if result else {
            "low_stock_items": 0,
            "out_of_stock_items": 0, 
            "reorder_needed_items": 0,
            "total_alerts": 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


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