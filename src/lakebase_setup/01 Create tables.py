# Databricks notebook source
# MAGIC %pip install -r requirements.txt
# MAGIC %restart_python

# COMMAND ----------

# MAGIC %load_ext autoreload
# MAGIC %autoreload 2

from lakebase_utils import LakebaseConnection

# COMMAND ----------

dbutils.widgets.text("user", "lars.liahagen@databricks.com")
username = dbutils.widgets.get("user")
dbutils.widgets.text("lakebase_instance_name", "smart-stock-db")
lakebase_instance_name = dbutils.widgets.get("lakebase_instance_name")

# COMMAND ----------

conn = LakebaseConnection(username, lakebase_instance_name)
conn.create_role_with_permissions("lakebase_demo_app", "lakebasedemo2025")

# COMMAND ----------

ddls = [
"DROP TABLE IF EXISTS inventory_transactions CASCADE;",
"DROP TABLE IF EXISTS inventory_historical CASCADE;"
"DROP TABLE IF EXISTS inventory_forecast CASCADE;",
"DROP TABLE IF EXISTS warehouses CASCADE;",
"DROP TABLE IF EXISTS products CASCADE;",
"""
CREATE TABLE warehouses (
	warehouse_id serial primary key,
	name varchar(100) not null,
	location varchar(200),
	manager_id integer,
	timezone varchar(50) default 'utc',
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""",
"""
CREATE TABLE products (
	product_id SERIAL primary key,
	name VARCHAR(100) not null,
	description text,
	sku varchar(50) unique not null,
	price decimal(10, 2) not null check (price >= 0),
	unit varchar(20) default 'piece',
	category varchar(50),
	reorder_level integer default 10,
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""",
"""
CREATE TABLE inventory_transactions (
	transaction_id serial primary key,
	transaction_number varchar(50) unique not null,
	product_id integer not null references products(product_id),
	warehouse_id integer not null references warehouses(warehouse_id),
	quantity_change integer not null,
	transaction_type varchar(50) check (transaction_type in ('inbound', 'sale', 'adjustment')),
	status varchar(20) default 'pending' check (status in ('pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled')),
	notes TEXT,
	transaction_timestamp timestamp default current_timestamp,
	updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""",
"""
CREATE TABLE inventory_historical (
	inventory_id serial primary key,
	product_id integer not null references products(product_id),
	warehouse_id integer not null references warehouses(warehouse_id),
	date date not null,
	inventory_level integer not null,
	updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""",
"""
CREATE TABLE inventory_forecast (
	forecast_id serial primary key,
	product_id integer not null references products(product_id),
	warehouse_id integer not null references warehouses(warehouse_id),
	current_stock integer,
	forecast_30_days integer,
	reorder_point integer,
	reorder_quantity integer,
	confidence_score DECIMAL(3, 2) CHECK (confidence_score >= 0 AND confidence_score <= 1),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'pending', 'expired')),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(product_id, warehouse_id)
);
""",
]

for ddl in ddls:
    conn.execute_statement(ddl)

# COMMAND ----------

conn.execute_query(f"SELECT * FROM pg_tables WHERE tableowner = '{username}'")
