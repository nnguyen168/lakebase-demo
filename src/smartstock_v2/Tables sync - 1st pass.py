# Databricks notebook source
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

# COMMAND ----------

# Dim Product
dim_product_pipeline_id = "8dd276d7-ddaf-48c1-905f-cd06ee3513e0"
dim_product_update = w.pipelines.start_update(pipeline_id=dim_product_pipeline_id, full_refresh=True)
print(f"Dim Product update ID: {dim_product_update.update_id}")

# COMMAND ----------

# Dim Warehouse
dim_warehouse_pipeline_id = "0835f41e-4248-474c-802c-a8b892643d61"
dim_warehouse_update = w.pipelines.start_update(pipeline_id=dim_warehouse_pipeline_id, full_refresh=True)
print(f"Dim Warehouse update ID: {dim_warehouse_update.update_id}")

# COMMAND ----------

# Inventory Transactions
inventory_transaction_pipeline_id = "41a42b76-489f-486e-8aa7-755d80a41f1d"
inventory_transaction_update = w.pipelines.start_update(pipeline_id=inventory_transaction_pipeline_id, full_refresh=True)
print(f"Inventory Transactions update ID: {inventory_transaction_update.update_id}")

# COMMAND ----------

# Inventory Historical
inventory_historical_pipeline_id = "bc27caff-b9bf-4af7-85d4-c7bbe178fa70"
inventory_historical_update = w.pipelines.start_update(pipeline_id=inventory_historical_pipeline_id, full_refresh=True)
print(f"Inventory Historical update ID: {inventory_historical_update.update_id}")