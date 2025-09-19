# Databricks notebook source
# MAGIC %pip install -r requirements.txt
# MAGIC %restart_python

# COMMAND ----------

# MAGIC %load_ext autoreload
# MAGIC %autoreload 2

from lakebase_utils import LakebaseConnection
from data_generator.data_generator import generate_data

# COMMAND ----------

dbutils.widgets.text("user", "lars.liahagen@databricks.com")
username = dbutils.widgets.get("user")
dbutils.widgets.text("lakebase_instance_name", "smart-stock-db")
lakebase_instance_name = dbutils.widgets.get("lakebase_instance_name")

conn = LakebaseConnection(username, lakebase_instance_name)

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC # Generate data

# COMMAND ----------

generate_data()

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC # Insert data

# COMMAND ----------

def csv_to_lakebase(file_path, table_name, lakebase_conn):
    with lakebase_conn.pool.connection() as conn:
        with conn.cursor() as cur:
            with open(file_path) as f:
                header = f.readline()
                with cur.copy(f"COPY {table_name}({header}) FROM stdin (format csv, delimiter ',')") as copy:
                    copy.write(f.read())

def reload_tables(conn):
    conn.execute_statement(
    """
    TRUNCATE TABLE inventory_transactions CASCADE;
    TRUNCATE TABLE inventory_historical CASCADE;
    TRUNCATE TABLE products CASCADE;
    TRUNCATE TABLE warehouses CASCADE;
    ALTER SEQUENCE inventory_transactions_transaction_id_seq RESTART WITH 1;
    ALTER SEQUENCE inventory_historical_inventory_id_seq RESTART WITH 1;
    ALTER SEQUENCE products_product_id_seq RESTART WITH 1;
    ALTER SEQUENCE warehouses_warehouse_id_seq RESTART WITH 1;
    """
    )
    csv_to_lakebase("data_generator/products.csv", "products", conn)
    csv_to_lakebase("data_generator/warehouses.csv", "warehouses", conn)
    csv_to_lakebase("data_generator/historical_transactions.csv", "inventory_transactions", conn)
    csv_to_lakebase("data_generator/historical_inventory_levels.csv", "inventory_historical", conn)

reload_tables(conn)

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC # Validate

# COMMAND ----------

conn.execute_query("SELECT * FROM products LIMIT 10")

# COMMAND ----------

conn.execute_query("SELECT * FROM warehouses LIMIT 10")

# COMMAND ----------

conn.execute_query("SELECT * FROM inventory_transactions LIMIT 10")

# COMMAND ----------

conn.execute_query("SELECT * FROM inventory_historical LIMIT 10")

# COMMAND ----------

conn.execute_query("SELECT COUNT(*) FROM inventory_transactions")