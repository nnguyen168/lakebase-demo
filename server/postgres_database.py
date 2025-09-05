"""PostgreSQL/Lakebase connection module."""

import os
import logging
from typing import Optional, Any, Dict, List
from contextlib import contextmanager
from pathlib import Path
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor

# Load environment variables only in development
# In production, environment variables come from app.yaml
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env.local'
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    # dotenv not available in production, which is fine
    pass

logger = logging.getLogger(__name__)


class LakebasePostgresConnection:
    """Manages connections to Lakebase (PostgreSQL-compatible) database."""
    
    def __init__(self):
        """Initialize Lakebase PostgreSQL connection pool."""
        self.db_config = {
            "host": os.getenv("DB_HOST"),
            "port": int(os.getenv("DB_PORT", 5432)),
            "database": os.getenv("DB_NAME", "inventory_demo"),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD"),
            "sslmode": "require",  # SSL is required for Lakebase
        }
        
        # Validate configuration
        if not all([self.db_config["host"], self.db_config["user"], self.db_config["password"]]):
            raise ValueError("DB_HOST, DB_USER, and DB_PASSWORD must be set in environment variables")
        
        # Create connection pool
        try:
            self.connection_pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=1,
                maxconn=20,
                **self.db_config
            )
            logger.info(f"Connected to Lakebase PostgreSQL at {self.db_config['host']}")
        except Exception as e:
            logger.error(f"Failed to create connection pool: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        connection = None
        try:
            connection = self.connection_pool.getconn()
            yield connection
        finally:
            if connection:
                self.connection_pool.putconn(connection)
    
    @contextmanager
    def get_cursor(self, dict_cursor=True):
        """Context manager for database cursor."""
        with self.get_connection() as conn:
            cursor = None
            try:
                cursor_factory = RealDictCursor if dict_cursor else None
                cursor = conn.cursor(cursor_factory=cursor_factory)
                yield cursor
                conn.commit()
            except Exception as e:
                conn.rollback()
                logger.error(f"Database error: {e}")
                raise
            finally:
                if cursor:
                    cursor.close()
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Execute a query and return results as list of dictionaries."""
        with self.get_cursor(dict_cursor=True) as cursor:
            cursor.execute(query, params)
            if cursor.description:
                return cursor.fetchall()
            return []
    
    def execute_update(self, query: str, params: Optional[tuple] = None) -> int:
        """Execute an update/insert/delete query and return affected rows."""
        with self.get_cursor(dict_cursor=False) as cursor:
            cursor.execute(query, params)
            return cursor.rowcount
    
    def create_tables(self):
        """Create all required tables for the inventory management system."""
        
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
            
            "inventory_history": """
                CREATE TABLE IF NOT EXISTS inventory_history (
                    history_id SERIAL PRIMARY KEY,
                    product_id INTEGER NOT NULL REFERENCES products(product_id),
                    store_id VARCHAR(50) NOT NULL,
                    quantity_change INTEGER NOT NULL,
                    transaction_type VARCHAR(20) NOT NULL,
                    reference_id VARCHAR(100),
                    notes TEXT,
                    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    balance_after INTEGER NOT NULL,
                    created_by VARCHAR(255) NOT NULL
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
                logger.info(f"Created/verified table {table_name}")
            except Exception as e:
                logger.error(f"Error creating table {table_name}: {e}")
                raise
        
        # Create indexes for better performance
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(order_date)",
            "CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status)",
            "CREATE INDEX IF NOT EXISTS idx_inventory_status ON inventory_forecast(status)",
            "CREATE INDEX IF NOT EXISTS idx_inventory_product_store ON inventory_forecast(product_id, store_id)",
        ]
        
        for index_ddl in indexes:
            try:
                self.execute_update(index_ddl)
            except Exception as e:
                logger.warning(f"Could not create index: {e}")
    
    def seed_sample_data(self):
        """Seed sample data for testing."""
        
        # Check if data already exists
        existing_customers = self.execute_query("SELECT COUNT(*) as count FROM customers")
        if existing_customers and existing_customers[0]['count'] > 0:
            logger.info("Data already exists, skipping seed")
            return
        
        # Insert sample customers
        customers = [
            ("John Doe", "john@example.com", "555-0101", "123 Main St"),
            ("Jane Smith", "jane@example.com", "555-0102", "456 Oak Ave"),
            ("Bob Johnson", "bob@example.com", "555-0103", "789 Pine Rd"),
        ]
        
        for customer in customers:
            self.execute_update(
                "INSERT INTO customers (name, email, phone, address) VALUES (%s, %s, %s, %s)",
                customer
            )
        
        # Insert sample products
        products = [
            ("Premium Coffee Beans", "Arabica beans from Colombia", "COF-001", 24.99, "lb", "Beverages"),
            ("Organic Green Tea", "Japanese matcha green tea", "TEA-001", 18.50, "box", "Beverages"),
            ("Sparkling Water", "Natural mineral water", "WAT-001", 2.99, "bottle", "Beverages"),
            ("Energy Drink", "High caffeine energy boost", "ENG-001", 3.99, "can", "Beverages"),
            ("Fresh Orange Juice", "100% pure orange juice", "JUI-001", 5.99, "bottle", "Beverages"),
        ]
        
        for product in products:
            self.execute_update(
                """INSERT INTO products (name, description, sku, price, unit, category) 
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                product
            )
        
        # Insert sample orders
        orders = [
            ("ORD-2024-001", 1, 1, "STORE-001", 10, "john.manager", "pending"),
            ("ORD-2024-002", 2, 2, "STORE-001", 5, "jane.manager", "approved"),
            ("ORD-2024-003", 3, 1, "STORE-002", 20, "bob.manager", "shipped"),
            ("ORD-2024-004", 4, 3, "STORE-002", 15, "john.manager", "pending"),
            ("ORD-2024-005", 5, 2, "STORE-003", 8, "jane.manager", "approved"),
        ]
        
        for order in orders:
            self.execute_update(
                """INSERT INTO orders (order_number, product_id, customer_id, store_id, quantity, requested_by, status) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                order
            )
        
        # Insert sample inventory forecast
        forecasts = [
            (1, "STORE-001", 100, 80, 20, 50, "in_stock"),
            (2, "STORE-001", 15, 25, 10, 30, "low_stock"),
            (3, "STORE-002", 200, 150, 50, 100, "in_stock"),
            (4, "STORE-002", 5, 40, 15, 50, "reorder_needed"),
            (5, "STORE-003", 0, 30, 10, 40, "out_of_stock"),
        ]
        
        for forecast in forecasts:
            self.execute_update(
                """INSERT INTO inventory_forecast (product_id, store_id, current_stock, forecast_30_days, 
                   reorder_point, reorder_quantity, status) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                forecast
            )
        
        logger.info("Sample data seeded successfully")
    
    def execute_order_transaction(self, action: str, order_data: dict):
        """Execute order transaction with inventory updates."""
        with self.get_cursor(dict_cursor=True) as cursor:
            if action == "create":
                return self._create_order_with_inventory(cursor, order_data)
            elif action == "cancel":
                return self._cancel_order_with_inventory(cursor, order_data)
            else:
                raise ValueError(f"Unknown action: {action}")
    
    def _create_order_with_inventory(self, cursor, order_data):
        """Create order and update inventory within transaction."""
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            # 1. Insert order
            order_query = """
                INSERT INTO orders (
                    order_number, product_id, customer_id, store_id, 
                    quantity, requested_by, status, notes
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING order_id
            """
            
            cursor.execute(order_query, [
                order_data["order_number"],
                order_data["product_id"],
                order_data["customer_id"],
                order_data["store_id"],
                order_data["quantity"],
                order_data["requested_by"],
                order_data["status"],
                order_data["notes"]
            ])
            
            order_result = cursor.fetchone()
            order_id = order_result['order_id']
            logger.info(f"Created order {order_id}")
            
            # 2. Update inventory forecast (decrease stock)
            inventory_update = """
                UPDATE inventory_forecast 
                SET current_stock = current_stock - %s,
                    last_updated = CURRENT_TIMESTAMP()
                WHERE product_id = %s AND store_id = %s
            """
            
            cursor.execute(inventory_update, [
                order_data["quantity"],
                order_data["product_id"],
                order_data["store_id"]
            ])
            
            # 3. Log inventory transaction
            history_insert = """
                INSERT INTO inventory_history (
                    product_id, store_id, quantity_change, transaction_type,
                    reference_id, notes, balance_after, created_by
                ) VALUES (
                    %s, %s, %s, 'OUT', %s, %s, 
                    (SELECT current_stock FROM inventory_forecast 
                     WHERE product_id = %s AND store_id = %s),
                    %s
                )
            """
            
            cursor.execute(history_insert, [
                order_data["product_id"],
                order_data["store_id"],
                -order_data["quantity"],  # Negative for outgoing
                order_data["order_number"],
                f"Order created: {order_data['order_number']}",
                order_data["product_id"],
                order_data["store_id"],
                order_data["requested_by"]
            ])
            
            logger.info(f"Updated inventory for order {order_data['order_number']}")
            
            # 4. Return created order with details
            final_query = """
                SELECT o.*, p.name as product_name, c.name as customer_name
                FROM orders o
                JOIN products p ON o.product_id = p.product_id
                JOIN customers c ON o.customer_id = c.customer_id
                WHERE o.order_id = %s
            """
            
            cursor.execute(final_query, [order_id])
            return cursor.fetchall()
            
        except Exception as e:
            logger.error(f"Order creation transaction failed: {e}")
            raise
    
    def _cancel_order_with_inventory(self, cursor, order_data):
        """Cancel order and rollback inventory within transaction."""
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            # 1. Update order status to cancelled
            order_update = """
                UPDATE orders 
                SET status = 'cancelled', updated_at = CURRENT_TIMESTAMP()
                WHERE order_id = %s
            """
            
            cursor.execute(order_update, [order_data["order_id"]])
            logger.info(f"Cancelled order {order_data['order_id']}")
            
            # 2. Rollback inventory (increase stock back)
            inventory_rollback = """
                UPDATE inventory_forecast 
                SET current_stock = current_stock + %s,
                    last_updated = CURRENT_TIMESTAMP()
                WHERE product_id = %s AND store_id = %s
            """
            
            cursor.execute(inventory_rollback, [
                order_data["quantity"],
                order_data["product_id"],
                order_data["store_id"]
            ])
            
            # 3. Log inventory rollback
            history_insert = """
                INSERT INTO inventory_history (
                    product_id, store_id, quantity_change, transaction_type,
                    reference_id, notes, balance_after, created_by
                ) VALUES (
                    %s, %s, %s, 'IN', %s, %s,
                    (SELECT current_stock FROM inventory_forecast 
                     WHERE product_id = %s AND store_id = %s),
                    'system'
                )
            """
            
            cursor.execute(history_insert, [
                order_data["product_id"],
                order_data["store_id"],
                order_data["quantity"],  # Positive for incoming
                order_data["order_number"],
                f"Order cancelled: {order_data['order_number']}",
                order_data["product_id"],
                order_data["store_id"]
            ])
            
            logger.info(f"Rolled back inventory for order {order_data['order_number']}")
            return True
            
        except Exception as e:
            logger.error(f"Order cancellation transaction failed: {e}")
            raise
    
    def close(self):
        """Close all connections in the pool."""
        if hasattr(self, 'connection_pool'):
            self.connection_pool.closeall()
            logger.info("Connection pool closed")


# Global database instance
db = LakebasePostgresConnection()