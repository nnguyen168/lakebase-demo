"""PostgreSQL/Lakebase connection module for food & beverage inventory."""

import os
import logging
from typing import Optional, Any, Dict, List
from contextlib import contextmanager
from pathlib import Path
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor

# Load environment variables only in development
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
            "database": os.getenv("DB_NAME", "databricks_postgres"),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD"),
            "sslmode": "require",  # SSL is required for Lakebase
        }

        # Get schema from environment
        self.schema = os.getenv("DB_SCHEMA", "public")

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
        """Create all required tables for the food & beverage inventory management system."""

        logger.info("Starting complete database schema creation...")

        # Drop all existing tables to start fresh
        drop_tables = [
            "DROP TABLE IF EXISTS stockout_events CASCADE",
            "DROP TABLE IF EXISTS inventory_forecast CASCADE",
            "DROP TABLE IF EXISTS inventory_history CASCADE",
            "DROP TABLE IF EXISTS inventory_current CASCADE",
            "DROP TABLE IF EXISTS orders CASCADE",
            "DROP TABLE IF EXISTS product_suppliers CASCADE",
            "DROP TABLE IF EXISTS suppliers CASCADE",
            "DROP TABLE IF EXISTS products CASCADE",
            "DROP TABLE IF EXISTS customers CASCADE",
            "DROP TABLE IF EXISTS stores CASCADE"
        ]

        for drop_stmt in drop_tables:
            try:
                self.execute_update(drop_stmt)
                logger.info(f"Dropped table: {drop_stmt}")
            except Exception as e:
                logger.warning(f"Error dropping table: {e}")

        # Create tables in correct dependency order

        # 1. Independent tables first (no foreign keys)
        stores_sql = """
            CREATE TABLE stores (
                store_id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                location VARCHAR(200),
                type VARCHAR(50) CHECK (type IN ('restaurant', 'warehouse', 'retail', 'cafe', 'food_truck')),
                manager_id INTEGER,
                timezone VARCHAR(50) DEFAULT 'UTC',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        self.execute_update(stores_sql)
        logger.info("Created stores table")

        customers_sql = """
            CREATE TABLE customers (
                customer_id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(150) UNIQUE,
                phone VARCHAR(20),
                address TEXT,
                customer_type VARCHAR(50) DEFAULT 'restaurant' CHECK (customer_type IN ('restaurant', 'hotel', 'catering', 'retail', 'individual')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        self.execute_update(customers_sql)
        logger.info("Created customers table")

        products_sql = """
            CREATE TABLE products (
                product_id SERIAL PRIMARY KEY,
                name VARCHAR(150) NOT NULL,
                description TEXT,
                sku VARCHAR(50) UNIQUE NOT NULL,
                price DECIMAL(10, 2) NOT NULL CHECK (price >= 0),
                unit VARCHAR(20) DEFAULT 'piece',
                category VARCHAR(50),
                reorder_level INTEGER DEFAULT 10,
                expiration_days INTEGER,
                storage_temp VARCHAR(50),
                allergens TEXT,
                organic BOOLEAN DEFAULT false,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        self.execute_update(products_sql)
        logger.info("Created products table")

        suppliers_sql = """
            CREATE TABLE suppliers (
                supplier_id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                contact_info JSONB,
                lead_time_days INTEGER DEFAULT 7,
                reliability_score DECIMAL(3, 2) CHECK (reliability_score >= 0 AND reliability_score <= 1),
                specialty VARCHAR(100),
                certifications TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        self.execute_update(suppliers_sql)
        logger.info("Created suppliers table")

        # 2. Tables with foreign keys
        orders_sql = """
            CREATE TABLE orders (
                order_id SERIAL PRIMARY KEY,
                order_number VARCHAR(50) UNIQUE NOT NULL,
                product_id INTEGER NOT NULL REFERENCES products(product_id),
                customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
                store_id INTEGER NOT NULL REFERENCES stores(store_id),
                quantity INTEGER NOT NULL CHECK (quantity > 0),
                requested_by VARCHAR(100),
                status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled')),
                notes TEXT,
                order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        self.execute_update(orders_sql)
        logger.info("Created orders table")

        product_suppliers_sql = """
            CREATE TABLE product_suppliers (
                product_id INTEGER REFERENCES products(product_id),
                supplier_id INTEGER REFERENCES suppliers(supplier_id),
                is_primary BOOLEAN DEFAULT false,
                unit_cost DECIMAL(10, 2) CHECK (unit_cost >= 0),
                min_order_qty INTEGER DEFAULT 1,
                last_order_date DATE,
                PRIMARY KEY (product_id, supplier_id)
            )
        """
        self.execute_update(product_suppliers_sql)
        logger.info("Created product_suppliers table")

        inventory_current_sql = """
            CREATE TABLE inventory_current (
                product_id INTEGER REFERENCES products(product_id),
                store_id INTEGER REFERENCES stores(store_id),
                quantity_on_hand INTEGER DEFAULT 0 CHECK (quantity_on_hand >= 0),
                quantity_available INTEGER DEFAULT 0 CHECK (quantity_available >= 0),
                quantity_reserved INTEGER DEFAULT 0 CHECK (quantity_reserved >= 0),
                last_counted_date DATE,
                last_count_by VARCHAR(100),
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (product_id, store_id)
            )
        """
        self.execute_update(inventory_current_sql)
        logger.info("Created inventory_current table")

        inventory_history_sql = """
            CREATE TABLE inventory_history (
                history_id SERIAL PRIMARY KEY,
                product_id INTEGER NOT NULL REFERENCES products(product_id),
                store_id INTEGER NOT NULL REFERENCES stores(store_id),
                quantity_change INTEGER NOT NULL,
                transaction_type VARCHAR(50) CHECK (transaction_type IN ('sale', 'purchase', 'return', 'adjustment', 'transfer_in', 'transfer_out', 'damage', 'theft', 'expired')),
                reference_id INTEGER,
                notes TEXT,
                transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                balance_after INTEGER,
                created_by VARCHAR(100)
            )
        """
        self.execute_update(inventory_history_sql)
        logger.info("Created inventory_history table")

        inventory_forecast_sql = """
            CREATE TABLE inventory_forecast (
                forecast_id SERIAL PRIMARY KEY,
                product_id INTEGER NOT NULL REFERENCES products(product_id),
                store_id INTEGER NOT NULL REFERENCES stores(store_id),
                current_stock INTEGER,
                forecast_30_days INTEGER,
                reorder_point INTEGER,
                reorder_quantity INTEGER,
                confidence_score DECIMAL(3, 2) CHECK (confidence_score >= 0 AND confidence_score <= 1),
                status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'pending', 'expired')),
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(product_id, store_id)
            )
        """
        self.execute_update(inventory_forecast_sql)
        logger.info("Created inventory_forecast table")

        stockout_events_sql = """
            CREATE TABLE stockout_events (
                event_id SERIAL PRIMARY KEY,
                product_id INTEGER NOT NULL REFERENCES products(product_id),
                store_id INTEGER NOT NULL REFERENCES stores(store_id),
                stockout_start TIMESTAMP NOT NULL,
                stockout_end TIMESTAMP,
                lost_sales_estimate DECIMAL(10, 2),
                root_cause VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        self.execute_update(stockout_events_sql)
        logger.info("Created stockout_events table")

        # Create indexes for better performance
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id)",
            "CREATE INDEX IF NOT EXISTS idx_orders_product ON orders(product_id)",
            "CREATE INDEX IF NOT EXISTS idx_orders_store ON orders(store_id)",
            "CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(order_date)",
            "CREATE INDEX IF NOT EXISTS idx_inventory_history_product_store ON inventory_history(product_id, store_id)",
            "CREATE INDEX IF NOT EXISTS idx_inventory_history_date ON inventory_history(transaction_date)",
            "CREATE INDEX IF NOT EXISTS idx_stockout_events_dates ON stockout_events(stockout_start, stockout_end)",
            "CREATE INDEX IF NOT EXISTS idx_products_category ON products(category)",
            "CREATE INDEX IF NOT EXISTS idx_products_expiration ON products(expiration_days)"
        ]

        for index_ddl in indexes:
            try:
                self.execute_update(index_ddl)
                logger.info(f"Created index: {index_ddl}")
            except Exception as e:
                logger.warning(f"Could not create index: {e}")

        logger.info("All enhanced food inventory tables created successfully")

    def seed_sample_data(self):
        """Seed comprehensive food & beverage sample data."""

        logger.info("Starting comprehensive food & beverage data seeding...")

        # 1. Insert stores first (no dependencies)
        stores_data = [
            ('Downtown Bistro', '123 Main St, Portland, OR 97201', 'restaurant', 1, 'America/Los_Angeles'),
            ('Central Food Warehouse', '456 Industrial Way, Portland, OR 97210', 'warehouse', 2, 'America/Los_Angeles'),
            ('Morning Glory Cafe', '789 Coffee Ave, Seattle, WA 98101', 'cafe', 3, 'America/Los_Angeles'),
            ('Gourmet Express Food Truck', 'Mobile Unit #1, Various Locations', 'food_truck', 4, 'America/Los_Angeles'),
            ('The Garden Restaurant', '321 Organic Blvd, San Francisco, CA 94105', 'restaurant', 5, 'America/Los_Angeles')
        ]

        for store in stores_data:
            self.execute_update(
                "INSERT INTO stores (name, location, type, manager_id, timezone) VALUES (%s, %s, %s, %s, %s)",
                store
            )
        logger.info("Inserted 5 stores")

        # 2. Insert customers (no dependencies)
        customers_data = [
            ('Pacific Northwest Hotels', 'orders@pnwhotels.com', '503-555-0101', '100 Hotel Row, Portland, OR', 'hotel'),
            ('Elite Catering Services', 'purchasing@elitecatering.com', '503-555-0102', '200 Event Plaza, Portland, OR', 'catering'),
            ('Sunshine Restaurant Group', 'supply@sunshinerestaurants.com', '206-555-0103', '300 Dining District, Seattle, WA', 'restaurant'),
            ('Mountain View Resort', 'kitchen@mvresort.com', '541-555-0104', '400 Resort Drive, Bend, OR', 'hotel'),
            ('Artisan Bakery Collective', 'ingredients@artisanbakery.com', '503-555-0105', '500 Baker Street, Portland, OR', 'retail')
        ]

        for customer in customers_data:
            self.execute_update(
                "INSERT INTO customers (name, email, phone, address, customer_type) VALUES (%s, %s, %s, %s, %s)",
                customer
            )
        logger.info("Inserted 5 customers")

        # 3. Insert comprehensive food products (no dependencies)
        products_data = [
            # Proteins
            ('Wild Salmon Fillets', 'Fresh Pacific Northwest salmon, sustainably caught', 'FISH-001', 24.99, 'lb', 'Seafood', 20, 3, 'Refrigerated (32-38°F)', 'Fish', False),
            ('Organic Chicken Breast', 'Free-range organic chicken breast', 'MEAT-001', 12.99, 'lb', 'Poultry', 30, 5, 'Refrigerated (32-38°F)', None, True),
            ('Grass-Fed Beef Ribeye', 'Premium grass-fed beef ribeye steaks', 'MEAT-002', 32.99, 'lb', 'Beef', 15, 7, 'Refrigerated (32-38°F)', None, True),
            ('Dungeness Crab Meat', 'Fresh local Dungeness crab meat', 'FISH-002', 45.99, 'lb', 'Seafood', 10, 2, 'Refrigerated (32-38°F)', 'Shellfish', False),
            ('Pork Tenderloin', 'Heritage breed pork tenderloin', 'MEAT-003', 18.99, 'lb', 'Pork', 25, 5, 'Refrigerated (32-38°F)', None, False),

            # Vegetables & Produce
            ('Organic Kale', 'Fresh organic lacinato kale', 'VEG-001', 3.99, 'bunch', 'Vegetables', 50, 7, 'Refrigerated (32-38°F)', None, True),
            ('Heirloom Tomatoes', 'Assorted heirloom tomatoes', 'VEG-002', 5.99, 'lb', 'Vegetables', 40, 5, 'Room Temperature', None, True),
            ('Baby Arugula', 'Fresh baby arugula greens', 'VEG-003', 4.99, '5oz container', 'Vegetables', 35, 5, 'Refrigerated (32-38°F)', None, True),
            ('Purple Top Turnips', 'Fresh purple top turnips', 'VEG-004', 2.99, 'lb', 'Vegetables', 30, 14, 'Cool Storage (45-50°F)', None, True),
            ('Shiitake Mushrooms', 'Fresh shiitake mushrooms', 'VEG-005', 8.99, 'lb', 'Mushrooms', 25, 7, 'Refrigerated (32-38°F)', None, True),

            # Dairy & Eggs
            ('Tillamook Cheddar', 'Sharp cheddar cheese from Tillamook', 'DAIRY-001', 7.99, 'lb', 'Cheese', 20, 30, 'Refrigerated (32-38°F)', 'Milk', False),
            ('Organic Free-Range Eggs', 'Large organic free-range eggs', 'DAIRY-002', 6.99, 'dozen', 'Eggs', 100, 21, 'Refrigerated (32-38°F)', 'Eggs', True),
            ('Heavy Whipping Cream', 'Organic heavy whipping cream', 'DAIRY-003', 4.99, '32oz', 'Dairy', 30, 14, 'Refrigerated (32-38°F)', 'Milk', True),
            ('Goat Cheese', 'Creamy local goat cheese', 'DAIRY-004', 12.99, 'lb', 'Cheese', 15, 21, 'Refrigerated (32-38°F)', 'Milk', True),
            ('Cultured Butter', 'European-style cultured butter', 'DAIRY-005', 8.99, 'lb', 'Dairy', 25, 45, 'Refrigerated (32-38°F)', 'Milk', True),

            # Pantry Items
            ('Arborio Rice', 'Premium Italian Arborio rice', 'GRAIN-001', 4.99, '2lb bag', 'Grains', 50, 365, 'Dry Storage', None, False),
            ('Organic Quinoa', 'Red and white quinoa blend', 'GRAIN-002', 8.99, '2lb bag', 'Grains', 40, 365, 'Dry Storage', None, True),
            ('Extra Virgin Olive Oil', 'Cold-pressed extra virgin olive oil', 'OIL-001', 19.99, '500ml', 'Oils', 30, 730, 'Cool, Dark Storage', None, True),
            ('Sea Salt', 'Coarse Pacific sea salt', 'SPICE-001', 3.99, '2lb container', 'Seasonings', 20, None, 'Dry Storage', None, False),
            ('Vanilla Extract', 'Pure Madagascar vanilla extract', 'EXTRACT-001', 24.99, '8oz bottle', 'Extracts', 15, 1095, 'Cool, Dark Storage', None, True),

            # Beverages
            ('Single Origin Coffee Beans', 'Colombian single origin coffee beans', 'BEV-001', 16.99, '2lb bag', 'Coffee', 40, 90, 'Cool, Dry Storage', None, True),
            ('Organic Black Tea', 'Premium organic black tea blend', 'BEV-002', 12.99, '1lb bag', 'Tea', 25, 730, 'Cool, Dry Storage', None, True),
            ('Pinot Noir Wine', 'Oregon Pinot Noir vintage', 'WINE-001', 28.99, '750ml bottle', 'Wine', 50, 1825, 'Cool Storage (55-60°F)', 'Sulfites', False),
            ('Craft IPA Beer', 'Local craft IPA 6-pack', 'BEER-001', 12.99, '6-pack', 'Beer', 60, 90, 'Refrigerated (32-38°F)', None, False),
            ('Sparkling Water', 'Natural sparkling water', 'BEV-003', 2.99, '1L bottle', 'Water', 100, 365, 'Room Temperature', None, False)
        ]

        for product in products_data:
            self.execute_update(
                """INSERT INTO products (name, description, sku, price, unit, category, reorder_level,
                   expiration_days, storage_temp, allergens, organic)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                product
            )
        logger.info("Inserted 23 comprehensive food products")

        # 4. Insert suppliers (no dependencies)
        suppliers_data = [
            ('Pacific Seafood Distributors', '{"email": "orders@pacificseafood.com", "phone": "503-555-0201", "address": "1000 Harbor Drive, Newport, OR"}', 2, 0.96, 'Fresh Seafood', 'MSC Certified, HACCP'),
            ('Oregon Organic Farms', '{"email": "wholesale@oregonorganic.com", "phone": "503-555-0202", "address": "2000 Farm Road, Hood River, OR"}', 3, 0.94, 'Organic Produce', 'USDA Organic, Demeter Biodynamic'),
            ('Columbia River Meats', '{"email": "sales@columbiarmeats.com", "phone": "503-555-0203", "address": "3000 Processing Plant Rd, The Dalles, OR"}', 5, 0.91, 'Premium Meats', 'USDA Inspected, Animal Welfare Approved'),
            ('Artisan Dairy Collective', '{"email": "orders@artisandairy.com", "phone": "503-555-0204", "address": "4000 Creamery Lane, Tillamook, OR"}', 2, 0.93, 'Artisan Dairy Products', 'Organic Certified, rBST Free'),
            ('Northwest Specialty Foods', '{"email": "purchasing@nwspecialty.com", "phone": "503-555-0205", "address": "5000 Gourmet Way, Portland, OR"}', 7, 0.89, 'Specialty Ingredients', 'SQF Certified, Non-GMO'),
            ('Cascade Coffee Roasters', '{"email": "wholesale@cascadecoffee.com", "phone": "503-555-0206", "address": "6000 Roastery Ave, Portland, OR"}', 1, 0.97, 'Coffee & Tea', 'Fair Trade, Organic, Rainforest Alliance')
        ]

        for supplier in suppliers_data:
            self.execute_update(
                "INSERT INTO suppliers (name, contact_info, lead_time_days, reliability_score, specialty, certifications) VALUES (%s, %s, %s, %s, %s, %s)",
                supplier
            )
        logger.info("Inserted 6 food suppliers")

        # 5. Insert product-supplier relationships (depends on products and suppliers)
        product_suppliers_data = [
            # Seafood from Pacific Seafood (supplier_id = 1)
            (1, 1, True, 18.50, 10, '2025-01-14'),
            (4, 1, True, 38.00, 5, '2025-01-13'),
            # Produce from Oregon Organic Farms (supplier_id = 2)
            (6, 2, True, 2.50, 25, '2025-01-14'),
            (7, 2, True, 4.20, 20, '2025-01-13'),
            (8, 2, True, 3.75, 30, '2025-01-12'),
            (9, 2, True, 2.10, 25, '2025-01-11'),
            (10, 2, True, 6.50, 15, '2025-01-10'),
            # Meats from Columbia River Meats (supplier_id = 3)
            (2, 3, True, 8.50, 20, '2025-01-12'),
            (3, 3, True, 26.00, 10, '2025-01-11'),
            (5, 3, True, 14.50, 15, '2025-01-10'),
            # Dairy from Artisan Dairy Collective (supplier_id = 4)
            (11, 4, True, 5.50, 10, '2025-01-14'),
            (12, 4, True, 4.20, 50, '2025-01-13'),
            (13, 4, True, 3.25, 20, '2025-01-12'),
            (14, 4, True, 8.75, 8, '2025-01-11'),
            (15, 4, True, 6.50, 12, '2025-01-10'),
            # Beverages from Cascade Coffee Roasters (supplier_id = 6)
            (20, 6, True, 12.50, 20, '2025-01-14'),
            (21, 6, True, 8.75, 15, '2025-01-13'),
            (22, 6, True, 19.50, 12, '2025-01-12'),
            (23, 6, True, 8.75, 24, '2025-01-11')
        ]

        for ps_data in product_suppliers_data:
            self.execute_update(
                "INSERT INTO product_suppliers (product_id, supplier_id, is_primary, unit_cost, min_order_qty, last_order_date) VALUES (%s, %s, %s, %s, %s, %s)",
                ps_data
            )
        logger.info("Inserted product-supplier relationships")

        # 6. Insert current inventory levels (depends on products and stores)
        inventory_current_data = [
            # Downtown Bistro (Store 1) - Full service restaurant
            (1, 1, 15, 12, 3, '2025-01-15', 'Chef Sarah'),
            (2, 1, 25, 20, 5, '2025-01-15', 'Chef Sarah'),
            (6, 1, 30, 25, 5, '2025-01-15', 'Chef Sarah'),
            (7, 1, 20, 18, 2, '2025-01-15', 'Chef Sarah'),
            (11, 1, 12, 10, 2, '2025-01-15', 'Chef Sarah'),
            (12, 1, 48, 40, 8, '2025-01-15', 'Chef Sarah'),
            # Central Food Warehouse (Store 2) - Distribution center
            (1, 2, 200, 200, 0, '2025-01-15', 'Warehouse Team'),
            (2, 2, 300, 300, 0, '2025-01-15', 'Warehouse Team'),
            (6, 2, 250, 250, 0, '2025-01-15', 'Warehouse Team'),
            (20, 2, 400, 400, 0, '2025-01-15', 'Warehouse Team'),
            # Morning Glory Cafe (Store 3) - Coffee shop
            (12, 3, 60, 50, 10, '2025-01-15', 'Manager Alex'),
            (20, 3, 45, 40, 5, '2025-01-15', 'Manager Alex'),
            (21, 3, 25, 20, 5, '2025-01-15', 'Manager Alex')
        ]

        for inventory in inventory_current_data:
            self.execute_update(
                "INSERT INTO inventory_current (product_id, store_id, quantity_on_hand, quantity_available, quantity_reserved, last_counted_date, last_count_by) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                inventory
            )
        logger.info("Inserted current inventory levels")

        # 7. Insert recent orders (depends on products, customers, stores)
        orders_data = [
            ('ORD-2025-F001', 1, 1, 1, 5, 'Pacific Northwest Hotels', 'delivered', 'Fresh salmon for weekend special', '2025-01-12 08:00:00'),
            ('ORD-2025-F002', 2, 2, 1, 10, 'Elite Catering Services', 'shipped', 'Wedding catering order - organic chicken', '2025-01-12 10:30:00'),
            ('ORD-2025-F003', 6, 3, 2, 50, 'Sunshine Restaurant Group', 'delivered', 'Weekly organic kale delivery', '2025-01-13 09:15:00'),
            ('ORD-2025-F004', 20, 3, 3, 10, 'Morning Glory Cafe', 'delivered', 'Coffee beans for weekend rush', '2025-01-13 11:45:00'),
            ('ORD-2025-F005', 7, 4, 1, 15, 'Mountain View Resort', 'processing', 'Heirloom tomatoes for farm dinner', '2025-01-13 14:20:00'),
            ('ORD-2025-F006', 12, 5, 1, 24, 'Artisan Bakery Collective', 'delivered', 'Free-range eggs for pastries', '2025-01-13 16:00:00')
        ]

        for order in orders_data:
            self.execute_update(
                "INSERT INTO orders (order_number, product_id, customer_id, store_id, quantity, requested_by, status, notes, order_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                order
            )
        logger.info("Inserted 6 food orders")

        # 8. Insert ML-generated inventory forecasts (depends on products and stores)
        forecasts_data = [
            # Downtown Bistro forecasts
            (1, 1, 15, 45, 10, 25, 0.92, 'active'),
            (2, 1, 25, 80, 15, 40, 0.89, 'active'),
            (6, 1, 30, 120, 20, 50, 0.91, 'active'),
            (7, 1, 20, 60, 15, 30, 0.88, 'active'),
            # Warehouse forecasts (higher volumes)
            (1, 2, 200, 600, 100, 300, 0.94, 'active'),
            (2, 2, 300, 900, 150, 400, 0.93, 'active'),
            (6, 2, 250, 800, 100, 300, 0.90, 'active'),
            # Cafe forecasts
            (20, 3, 45, 180, 25, 60, 0.96, 'active'),
            (21, 3, 25, 75, 15, 30, 0.87, 'active')
        ]

        for forecast in forecasts_data:
            self.execute_update(
                "INSERT INTO inventory_forecast (product_id, store_id, current_stock, forecast_30_days, reorder_point, reorder_quantity, confidence_score, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                forecast
            )
        logger.info("Inserted inventory forecasts")

        # 9. Insert some stockout events for analysis (depends on products and stores)
        stockout_events_data = [
            (4, 1, '2025-01-08 14:00:00', '2025-01-09 10:00:00', 183.96, 'Dungeness crab delivery delayed due to weather'),
            (20, 3, '2025-01-10 09:00:00', '2025-01-10 16:00:00', 135.92, 'Coffee roaster equipment malfunction'),
            (7, 1, '2025-01-11 12:00:00', '2025-01-12 08:00:00', 89.85, 'Organic tomato supplier truck breakdown')
        ]

        for stockout in stockout_events_data:
            self.execute_update(
                "INSERT INTO stockout_events (product_id, store_id, stockout_start, stockout_end, lost_sales_estimate, root_cause) VALUES (%s, %s, %s, %s, %s, %s)",
                stockout
            )
        logger.info("Inserted stockout events")

        logger.info("✅ Comprehensive food & beverage inventory system seeded successfully!")
        logger.info("📊 Created: 5 stores, 5 customers, 23 products, 6 suppliers, 19 supplier relationships")
        logger.info("📈 Added: current inventory, orders, forecasts, and stockout analytics")

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

            # 2. Update inventory current (decrease available stock)
            inventory_update = """
                UPDATE inventory_current
                SET quantity_available = quantity_available - %s,
                    quantity_reserved = quantity_reserved + %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE product_id = %s AND store_id = %s
            """

            cursor.execute(inventory_update, [
                order_data["quantity"],
                order_data["quantity"],
                order_data["product_id"],
                order_data["store_id"]
            ])

            # Also update forecast current stock
            forecast_update = """
                UPDATE inventory_forecast
                SET current_stock = current_stock - %s,
                    last_updated = CURRENT_TIMESTAMP
                WHERE product_id = %s AND store_id = %s
            """

            cursor.execute(forecast_update, [
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
                    %s, %s, %s, 'sale', %s, %s,
                    (SELECT quantity_on_hand FROM inventory_current
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
                SELECT o.*, p.name as product_name, c.name as customer_name, s.name as store_name
                FROM orders o
                JOIN products p ON o.product_id = p.product_id
                JOIN customers c ON o.customer_id = c.customer_id
                JOIN stores s ON o.store_id = s.store_id
                WHERE o.order_id = %s
            """

            cursor.execute(final_query, [order_id])
            return cursor.fetchall()

        except Exception as e:
            logger.error(f"Order creation transaction failed: {e}")
            raise

    def _cancel_order_with_inventory(self, cursor, order_data):
        """Cancel order and rollback inventory within transaction."""
        try:
            # 1. Update order status to cancelled
            order_update = """
                UPDATE orders
                SET status = 'cancelled', updated_at = CURRENT_TIMESTAMP
                WHERE order_id = %s
            """

            cursor.execute(order_update, [order_data["order_id"]])
            logger.info(f"Cancelled order {order_data['order_id']}")

            # 2. Rollback inventory (increase stock back)
            inventory_rollback = """
                UPDATE inventory_current
                SET quantity_available = quantity_available + %s,
                    quantity_reserved = quantity_reserved - %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE product_id = %s AND store_id = %s
            """

            cursor.execute(inventory_rollback, [
                order_data["quantity"],
                order_data["quantity"],
                order_data["product_id"],
                order_data["store_id"]
            ])

            # Also rollback forecast
            forecast_rollback = """
                UPDATE inventory_forecast
                SET current_stock = current_stock + %s,
                    last_updated = CURRENT_TIMESTAMP
                WHERE product_id = %s AND store_id = %s
            """

            cursor.execute(forecast_rollback, [
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
                    %s, %s, %s, 'return', %s, %s,
                    (SELECT quantity_on_hand FROM inventory_current
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