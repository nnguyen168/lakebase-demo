# Databricks notebook source
# MAGIC %pip install psycopg[binary,pool] databricks-sdk>=0.65.0
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
dbutils.widgets.text("catalog", "smart_stock")
catalog = dbutils.widgets.get("catalog")
dbutils.widgets.text("schema_silver", "smart_stock_silver")
schema_silver = dbutils.widgets.get("schema_silver")

conn = LakebaseConnection(username, lakebase_instance_name)


# COMMAND ----------

df_transactions = conn.execute_query("SELECT * FROM inventory_transactions")
df_transactions.head(10)

# COMMAND ----------

df_products = conn.execute_query("SELECT * FROM products")
df_warehouses = conn.execute_query("SELECT * FROM warehouses")
df_historical_inventory = conn.execute_query("SELECT * FROM inventory_historical")

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC ## Calculate inventory and sales history

# COMMAND ----------

historical_sales_query = """
WITH RECURSIVE all_dates(transaction_date) AS (
    SELECT MIN(DATE(transaction_timestamp))::date AS transaction_date
    FROM inventory_transactions
    UNION ALL
    SELECT (transaction_date + INTERVAL '1 day')::date
    FROM all_dates
    WHERE (transaction_date + INTERVAL '1 day')::date <= (
        SELECT MAX(DATE(transaction_timestamp))::date FROM inventory_transactions
    )
),
warehouse_products AS (
    SELECT DISTINCT warehouse_id, product_id FROM inventory_transactions
),
daily_inventory AS (
    SELECT
        warehouse_id,
        product_id,
        DATE(transaction_timestamp) AS transaction_date,
        SUM(quantity_change) AS daily_quantity_change
    FROM inventory_transactions
    WHERE transaction_type = 'sale'
    GROUP BY warehouse_id, product_id, DATE(transaction_timestamp)
),
calendar AS (
    SELECT
        wp.warehouse_id,
        wp.product_id,
        ad.transaction_date
    FROM warehouse_products wp
    CROSS JOIN all_dates ad
),
weekly_sales AS (
    SELECT
        c.warehouse_id,
        c.product_id,
        DATE_TRUNC('week', c.transaction_date) AS week_start,
        COALESCE(-di.daily_quantity_change, 0) AS daily_sales
    FROM calendar c
    LEFT JOIN daily_inventory di
        ON c.warehouse_id = di.warehouse_id
        AND c.product_id = di.product_id
        AND c.transaction_date = di.transaction_date
)
SELECT
    warehouse_id,
    product_id,
    week_start,
    SUM(daily_sales) AS weekly_sales
FROM weekly_sales
GROUP BY warehouse_id, product_id, week_start
ORDER BY warehouse_id, product_id, week_start
"""
df_historical_sales = conn.execute_query(historical_sales_query)
df_historical_sales.head(10)

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC ## Write to Delta

# COMMAND ----------

spark.sql(f"CREATE CATALOG IF NOT EXISTS {catalog}")
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {catalog}.{schema_silver}")

# COMMAND ----------

sdf_historical_sales = spark.createDataFrame(df_historical_sales)
sdf_historical_sales.write.mode("overwrite").saveAsTable(f"{catalog}.{schema_silver}.sales_history")

# COMMAND ----------

spark.createDataFrame(df_products).write.mode("overwrite").saveAsTable(f"{catalog}.{schema_silver}.products")
spark.createDataFrame(df_warehouses).write.mode("overwrite").saveAsTable(f"{catalog}.{schema_silver}.warehouses")
spark.createDataFrame(df_historical_inventory).write.mode("overwrite").saveAsTable(f"{catalog}.{schema_silver}.inventory_history")