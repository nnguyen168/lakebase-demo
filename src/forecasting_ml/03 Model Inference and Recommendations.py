# Databricks notebook source
# MAGIC %md
# MAGIC %md
# MAGIC # Sales Forecasting and Restocking Recommendations Pipeline
# MAGIC
# MAGIC This notebook implements an end-to-end workflow for generating sales forecasts and restocking recommendations for each warehouse and product. The process included:
# MAGIC
# MAGIC 1. **Loading Models and Preparing Data:**
# MAGIC    * Loaded MLflow models for each warehouse.
# MAGIC    * Read historical sales data and identified all (warehouse_id, product_id) pairs and week_start dates.
# MAGIC 2. **Generating Forecasts:**
# MAGIC    * Produced forecasts for all historical and 6 future weeks for each warehouse/product using the loaded models.
# MAGIC    * Wrote the results to the `lars_dev.forecast.sales_forecast` table.
# MAGIC 3. **Restocking Recommendations:**
# MAGIC    * Sampled and explored both the forecast and inventory tables to confirm schemas.
# MAGIC    * Calculated the sum of forecasted sales for the next 4 weeks and compared it to the most recent inventory levels.
# MAGIC    * Recommended restocking for any (warehouse_id, product_id) where inventory is predicted to run out in the next 4 weeks.
# MAGIC    * Wrote 71 restocking recommendations to the `lars_dev.forecast.inventory_forecast` table, including columns: warehouse_id, product_id, inventory_level, forecast_4w, restock_qty.
# MAGIC
# MAGIC **Next Steps:**
# MAGIC * Review the `inventory_forecast` table for actionable restocking decisions.
# MAGIC * Adjust forecast horizon or restocking logic as needed for your business requirements.
# MAGIC
# MAGIC _This pipeline is ready for productionization and further automation._

# COMMAND ----------

# MAGIC %pip install mlflow-skinny=3.3.2
# MAGIC %restart_python

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1: Load Models and Prepare Data
# MAGIC Load trained models for each warehouse from MLflow and read historical sales data. Identify all unique (warehouse_id, product_id) pairs and the full range of historical week_start dates for forecasting.

# COMMAND ----------

import mlflow
import pandas as pd
from pyspark.sql import functions as F
from pyspark.sql.types import TimestampType
from datetime import timedelta
from pyspark.sql import Window

# COMMAND ----------

dbutils.widgets.text("catalog", "smart_stock")
catalog = dbutils.widgets.get("catalog")
dbutils.widgets.text("schema_silver", "silver")
schema_silver = dbutils.widgets.get("schema_silver")
dbutils.widgets.text("schema_forecast", "forecast")
schema_forecast = dbutils.widgets.get("schema_forecast")

# COMMAND ----------

# Read historical sales data (limit to last 3 years for efficiency)
sales_history = spark.read.table(f"{catalog}.{schema_silver}.sales_history") \
    .filter(F.col('week_start') >= F.date_sub(F.current_date(), 7*52*3))

# Get unique (warehouse_id, product_id) pairs and all week_start dates
unique_pairs = sales_history.select('warehouse_id', 'product_id').distinct().toPandas()
unique_warehouse_ids = unique_pairs['warehouse_id'].unique()
all_weeks = sales_history.select('week_start').distinct().toPandas()['week_start'].sort_values().tolist()

# Prepare a dictionary to hold loaded models for each warehouse
warehouse_models = {}

# Load Unity Catalog model with alias 'champion' for each warehouse
for wid in unique_pairs['warehouse_id'].unique():
    model_name = f"{catalog}.{schema_forecast}.warehouse_forecast_{wid}"
    try:
        warehouse_models[wid] = mlflow.pyfunc.load_model(f"models:/{model_name}@champion")
    except Exception:
        pass

if not warehouse_models:
    raise ValueError("No models loaded. Check model registry and warehouse IDs.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2: Generate Forecasts for All Historical Dates Plus 6 Weeks Ahead
# MAGIC For each warehouse and product, generate predictions for all historical week_start dates plus 6 future weeks. Assemble a DataFrame with columns: warehouse_id, product_id, week_start, forecast.

# COMMAND ----------



# Prepare forecast horizon: all historical weeks + 6 future weeks
df_weeks = pd.DataFrame({'week_start': all_weeks})
last_week = pd.to_datetime(df_weeks['week_start']).max()
future_weeks = [last_week + timedelta(weeks=i) for i in range(1, 7)]
all_forecast_weeks = pd.to_datetime(df_weeks['week_start']).tolist() + future_weeks

# Prepare forecast input DataFrame for each warehouse
forecast_results = []
warehouse_inputs = {
    wid: { "product_id": [], "week_start": [] }
    for wid in unique_warehouse_ids
}
for row in unique_pairs.itertuples():
    wid = row.warehouse_id
    pid = row.product_id
    warehouse_inputs[wid]['product_id'].extend([pid]*len(all_forecast_weeks))
    warehouse_inputs[wid]['week_start'].extend(all_forecast_weeks)

for wid in unique_warehouse_ids:
    model = warehouse_models.get(wid)
    if model is None:
        continue
    # Prepare input DataFrame for this warehouse
    input_df = pd.DataFrame(warehouse_inputs[wid])
    # Predict
    try:
        preds = model.predict(input_df)
        preds['warehouse_id'] = wid
        forecast_results.append(preds)
    except Exception:
        pass

if not forecast_results:
    raise ValueError("No forecast results were generated. Check model loading and prediction logic.")

# Combine all forecasts into a single DataFrame
forecast_df = pd.concat(forecast_results, ignore_index=True)
forecast_df = forecast_df[['warehouse_id', 'product_id', 'week_start', 'prediction']].rename(columns={'prediction': 'forecast'})

# COMMAND ----------

# MAGIC %md
# MAGIC %md
# MAGIC ## Step 3: Write Forecasts to Table
# MAGIC Convert the pandas DataFrame to a Spark DataFrame, ensure correct types, and write to the target table, overwriting existing data.

# COMMAND ----------

# Ensure correct dtypes in pandas DataFrame
df = forecast_df.copy()
df['warehouse_id'] = df['warehouse_id'].astype(int)
df['product_id'] = df['product_id'].astype(int)
df['forecast'] = df['forecast'].astype(float)
df['week_start'] = pd.to_datetime(df['week_start'])

# Convert to Spark DataFrame
spark_df = spark.createDataFrame(df)

# Ensure week_start is timestamp
target_df = spark_df.withColumn('week_start', F.col('week_start').cast(TimestampType()))

# Write to table, overwrite mode
target_df.write.mode('overwrite').saveAsTable(f"{catalog}.{schema_forecast}.sales_forecast")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4: Calculate Restocking Recommendations
# MAGIC Join the most recent inventory levels with the 4-week forecast sums, and recommend restocking if inventory will run out. Prepare the result for writing.

# COMMAND ----------

# 1. Get most recent inventory_level for each (warehouse_id, product_id)
inv = spark.read.table(f"{catalog}.{schema_silver}.inventory_history")
window = Window.partitionBy('warehouse_id', 'product_id').orderBy(F.col('date').desc())
latest_inv = inv.withColumn('rn', F.row_number().over(window)) \
    .filter(F.col('rn') == 1) \
    .select('warehouse_id', 'product_id', 'inventory_level')

# 2. Sum forecast for next 4 weeks for each (warehouse_id, product_id)

forecast = spark.read.table(f"{catalog}.{schema_forecast}.sales_forecast")
future_4w = forecast \
    .filter(F.col('week_start') >= F.current_date()) \
    .filter(F.col('week_start') < F.date_add(F.current_date(), 28)) \
    .groupBy('warehouse_id', 'product_id') \
    .agg(F.sum('forecast').alias('forecast_4w'))

# 3. Join and calculate restock recommendation
rec = latest_inv.join(future_4w, ['warehouse_id', 'product_id'], 'inner') \
    .withColumn('restock_needed', F.col('inventory_level') - F.col('forecast_4w') <= 0) \
    .withColumn('restock_qty', F.when(F.col('restock_needed'), F.col('forecast_4w') - F.col('inventory_level')).otherwise(F.lit(0))) \
    .withColumn('restock_qty', F.round(F.col('restock_qty')).cast('long'))

# 4. Only keep recommendations where restock is needed
rec_final = rec.filter(F.col('restock_needed')).select(
    'warehouse_id', 'product_id', 'inventory_level', 'forecast_4w', 'restock_qty'
)
display(rec_final)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 5: Write Restocking Recommendations to Table
# MAGIC Write the restocking recommendations DataFrame to the lars_dev.forecast.inventory_forecast table, overwriting any existing data. This will make the recommendations available for downstream use.

# COMMAND ----------

# Write recommendations to lars_dev.forecast.inventory_forecast (overwrite mode)
rec_final.write.mode('overwrite').saveAsTable(f"{catalog}.{schema_forecast}.inventory_forecast")