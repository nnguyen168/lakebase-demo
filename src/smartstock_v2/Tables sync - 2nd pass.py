# Databricks notebook source
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

# COMMAND ----------

dbutils.widgets.text("inventory_forecast_pipeline_id", "")

inventory_forecast_pipeline_id = dbutils.widgets.get("inventory_forecast_pipeline_id")

# COMMAND ----------

# Inventory forecast
inventory_forecast_update = w.pipelines.start_update(pipeline_id=inventory_forecast_pipeline_id, full_refresh=True)
print(f"Inventory Forecast update ID: {inventory_forecast_update.update_id}")