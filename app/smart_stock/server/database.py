"""Database connection and table creation for Lakebase."""

import os
from typing import Optional, Any, Dict, List
from contextlib import contextmanager
import logging
from databricks import sql
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.catalog import SchemaInfo, TableInfo

logger = logging.getLogger(__name__)


class LakebaseConnection:
    """Manages connections to Databricks Lakebase."""
    
    def __init__(self):
        """Initialize Lakebase connection parameters."""
        self.host = os.getenv("DATABRICKS_HOST", "").rstrip("/")
        self.token = os.getenv("DATABRICKS_TOKEN", "")
        self.http_path = os.getenv("DATABRICKS_HTTP_PATH", "")
        self.catalog = os.getenv("DATABRICKS_CATALOG", "main")
        self.schema = os.getenv("DATABRICKS_SCHEMA", "inventory_demo")
        
        if not all([self.host, self.token]):
            raise ValueError("DATABRICKS_HOST and DATABRICKS_TOKEN must be set")
        
        # Initialize Workspace Client for catalog operations
        self.workspace_client = WorkspaceClient(
            host=self.host,
            token=self.token
        )
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        connection = None
        try:
            connection = sql.connect(
                server_hostname=self.host.replace("https://", "").replace("http://", ""),
                http_path=self.http_path,
                access_token=self.token,
                catalog=self.catalog,
                schema=self.schema
            )
            yield connection
        finally:
            if connection:
                connection.close()
    
    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute a query and return results as list of dictionaries."""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                if cursor.description:
                    columns = [desc[0] for desc in cursor.description]
                    return [dict(zip(columns, row)) for row in cursor.fetchall()]
                return []
    
    def execute_update(self, query: str, params: Optional[Dict[str, Any]] = None) -> int:
        """Execute an update/insert/delete query and return affected rows."""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                return cursor.rowcount
    
    def create_schema_if_not_exists(self):
        """Create the schema if it doesn't exist."""
        try:
            self.workspace_client.schemas.create(
                name=self.schema,
                catalog_name=self.catalog
            )
            logger.info(f"Created schema {self.catalog}.{self.schema}")
        except Exception as e:
            if "already exists" in str(e).lower():
                logger.info(f"Schema {self.catalog}.{self.schema} already exists")
            else:
                raise
    
    def create_tables(self):
        """Create all required tables for the inventory management system."""
        
        # Create schema first
        self.create_schema_if_not_exists()
        
        # Table creation DDL statements
        tables = {
            "customers": """
                CREATE TABLE IF NOT EXISTS customers (
                    customer_id BIGINT GENERATED ALWAYS AS IDENTITY,
                    name STRING NOT NULL,
                    email STRING NOT NULL,
                    phone STRING,
                    address STRING,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
                    CONSTRAINT pk_customers PRIMARY KEY(customer_id)
                )
            """,
            
            "products": """
                CREATE TABLE IF NOT EXISTS products (
                    product_id BIGINT GENERATED ALWAYS AS IDENTITY,
                    name STRING NOT NULL,
                    description STRING,
                    sku STRING NOT NULL,
                    price DECIMAL(10, 2) NOT NULL,
                    unit STRING DEFAULT 'unit',
                    category STRING,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
                    CONSTRAINT pk_products PRIMARY KEY(product_id),
                    CONSTRAINT uk_products_sku UNIQUE(sku)
                )
            """,
            
            "orders": """
                CREATE TABLE IF NOT EXISTS orders (
                    order_id BIGINT GENERATED ALWAYS AS IDENTITY,
                    order_number STRING NOT NULL,
                    product_id BIGINT NOT NULL,
                    customer_id BIGINT NOT NULL,
                    store_id STRING NOT NULL,
                    quantity INT NOT NULL,
                    requested_by STRING NOT NULL,
                    status STRING DEFAULT 'pending',
                    notes STRING,
                    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
                    CONSTRAINT pk_orders PRIMARY KEY(order_id),
                    CONSTRAINT uk_orders_number UNIQUE(order_number),
                    CONSTRAINT fk_orders_product FOREIGN KEY(product_id) REFERENCES products(product_id),
                    CONSTRAINT fk_orders_customer FOREIGN KEY(customer_id) REFERENCES customers(customer_id)
                )
            """,
            
            "inventory_history": """
                CREATE TABLE IF NOT EXISTS inventory_history (
                    history_id BIGINT GENERATED ALWAYS AS IDENTITY,
                    product_id BIGINT NOT NULL,
                    store_id STRING NOT NULL,
                    quantity_change INT NOT NULL,
                    transaction_type STRING NOT NULL,
                    reference_id STRING,
                    notes STRING,
                    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
                    balance_after INT NOT NULL,
                    created_by STRING NOT NULL,
                    CONSTRAINT pk_inventory_history PRIMARY KEY(history_id),
                    CONSTRAINT fk_inventory_history_product FOREIGN KEY(product_id) REFERENCES products(product_id)
                )
            """,
            
            "inventory_forecast": """
                CREATE TABLE IF NOT EXISTS inventory_forecast (
                    forecast_id BIGINT GENERATED ALWAYS AS IDENTITY,
                    product_id BIGINT NOT NULL,
                    store_id STRING NOT NULL,
                    current_stock INT NOT NULL,
                    forecast_30_days INT NOT NULL,
                    reorder_point INT NOT NULL,
                    reorder_quantity INT NOT NULL,
                    status STRING NOT NULL,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
                    CONSTRAINT pk_inventory_forecast PRIMARY KEY(forecast_id),
                    CONSTRAINT fk_inventory_forecast_product FOREIGN KEY(product_id) REFERENCES products(product_id),
                    CONSTRAINT uk_forecast_product_store UNIQUE(product_id, store_id)
                )
            """
        }
        
        # Create each table
        for table_name, ddl in tables.items():
            try:
                self.execute_update(ddl)
                logger.info(f"Created table {table_name}")
            except Exception as e:
                logger.error(f"Error creating table {table_name}: {e}")
                raise
    
    def seed_sample_data(self):
        """Seed sample data for testing."""
        
        # Insert sample customers
        customers = [
            ("John Doe", "john@example.com", "555-0101", "123 Main St"),
            ("Jane Smith", "jane@example.com", "555-0102", "456 Oak Ave"),
            ("Bob Johnson", "bob@example.com", "555-0103", "789 Pine Rd"),
        ]
        
        for customer in customers:
            self.execute_update(
                """INSERT INTO customers (name, email, phone, address) 
                   VALUES (?, ?, ?, ?)""",
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
                   VALUES (?, ?, ?, ?, ?, ?)""",
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
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
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
                """INSERT INTO inventory_forecast (product_id, store_id, current_stock, forecast_30_days, reorder_point, reorder_quantity, status) 
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                forecast
            )
        
        logger.info("Sample data seeded successfully")


# Global database instance
db = LakebaseConnection()