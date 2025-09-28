"""Debug endpoint to check database connection."""

import os
import psycopg2
from fastapi import APIRouter

router = APIRouter(prefix="/debug", tags=["debug"])

@router.get("/test-products")
async def test_products():
    """Direct test of products query."""
    import psycopg2
    from psycopg2.extras import RealDictCursor

    result = {
        "env": {
            "DB_HOST": os.getenv("DB_HOST", "NOT SET"),
            "DB_USER": os.getenv("DB_USER", "NOT SET"),
        },
        "direct_query": None,
        "via_db_module": None,
        "error": None
    }

    # Try direct query
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT", 5432),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT COUNT(*) as count FROM products")
        result["direct_query"] = cur.fetchone()
        cur.close()
        conn.close()
    except Exception as e:
        result["error"] = f"Direct query failed: {str(e)}"

    # Try via db module
    try:
        from ..db_selector import db
        products = db.execute_query("SELECT COUNT(*) as count FROM products")
        result["via_db_module"] = products[0] if products else None
    except Exception as e:
        result["error"] = f"DB module query failed: {str(e)}"

    return result

@router.get("/db-status")
async def check_db_status():
    """Check database connection status and configuration."""

    # Check environment variables
    env_vars = {
        "DB_HOST": os.getenv("DB_HOST", "NOT SET"),
        "DB_PORT": os.getenv("DB_PORT", "NOT SET"),
        "DB_NAME": os.getenv("DB_NAME", "NOT SET"),
        "DB_USER": os.getenv("DB_USER", "NOT SET"),
        "DB_PASSWORD": "***" if os.getenv("DB_PASSWORD") else "NOT SET",
        "DB_SSL_MODE": os.getenv("DB_SSL_MODE", "prefer (default)"),
    }

    # Try to connect and run a simple query
    connection_status = "Unknown"
    error_message = None
    product_count = None
    warehouse_count = None
    connection_details = {}

    try:
        from ..db_selector import db

        # Test query
        products = db.execute_query("SELECT COUNT(*) as count FROM products")
        product_count = products[0]['count'] if products else 0

        warehouses = db.execute_query("SELECT COUNT(*) as count FROM warehouses")
        warehouse_count = warehouses[0]['count'] if warehouses else 0

        connection_status = "Connected via db_selector"
    except Exception as e:
        connection_status = "Failed via db_selector"
        error_message = str(e)

        # Try direct connection to get more details
        try:
            conn_str = f"host={os.getenv('DB_HOST')} port={os.getenv('DB_PORT', 5432)} dbname={os.getenv('DB_NAME')} user={os.getenv('DB_USER')} password={os.getenv('DB_PASSWORD')}"

            # Try without SSL first
            try:
                conn = psycopg2.connect(conn_str)
                connection_details["direct_no_ssl"] = "Success"
                conn.close()
            except Exception as e:
                connection_details["direct_no_ssl"] = f"Failed: {str(e)[:100]}"

            # Try with SSL
            try:
                conn = psycopg2.connect(conn_str + " sslmode=require")
                connection_details["direct_with_ssl"] = "Success"
                conn.close()
            except Exception as e:
                connection_details["direct_with_ssl"] = f"Failed: {str(e)[:100]}"

        except Exception as e:
            connection_details["direct_connection"] = f"Failed: {str(e)[:100]}"

    return {
        "status": connection_status,
        "error": error_message,
        "environment": env_vars,
        "data": {
            "products": product_count,
            "warehouses": warehouse_count
        },
        "connection_tests": connection_details
    }