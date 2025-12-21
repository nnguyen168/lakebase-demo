# Databricks notebook source
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

# COMMAND ----------

# Inventory forecast
inventory_forecast_pipeline_id = "e69fb378-312a-4ec1-9765-03c6222c222d"
inventory_forecast_update = w.pipelines.start_update(pipeline_id=inventory_forecast_pipeline_id, full_refresh=True)
print(f"Inventory Forecast update ID: {inventory_forecast_update.update_id}")