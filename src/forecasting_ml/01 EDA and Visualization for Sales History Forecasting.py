# Databricks notebook source
# MAGIC %md
# MAGIC # Sales History EDA & Visualization: Notebook Overview and Results
# MAGIC
# MAGIC This notebook explores weekly sales data from the last 3 years for the top 5 most active (warehouse_id, product_id) pairs in [lars_dev.smart_stock_silver.sales_history](#table) on AWS Databricks. The workflow includes:
# MAGIC
# MAGIC * **Data Sampling:** Extracts and inspects recent sales data, focusing on the most active product/warehouse pairs.
# MAGIC * **Automated Profiling:** Uses ydata-profiling to summarize distributions, missing values, and correlations.
# MAGIC * **Visualization:** Plots weekly sales trends for selected pairs, revealing seasonality, trends, and outliers.
# MAGIC
# MAGIC **Key Results:**
# MAGIC * Data is well-structured for time series forecasting, with clear weekly granularity and minimal missingness.
# MAGIC * Visualizations show significant week-to-week variability and some seasonal patterns, supporting the use of advanced forecasting models.
# MAGIC * The notebook is organized for easy extension to feature engineering and model training.
# MAGIC
# MAGIC _Proceed to the next sections for detailed code, EDA, and visualizations._

# COMMAND ----------
dbutils.widgets.text("catalog", "lars_lia")
catalog = dbutils.widgets.get("catalog")
dbutils.widgets.text("schema_silver", "smart_stock_silver")
schema_silver = dbutils.widgets.get("schema_silver")

# COMMAND ----------

# Install ydata-profiling if not already installed
try:
    import ydata_profiling
except ImportError:
    %pip install ydata-profiling==4.8.3

# No need to install matplotlib, seaborn, pandas on Databricks, but can be added if needed


# COMMAND ----------

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from pyspark.sql.functions import col
from pyspark.sql import DataFrame
from functools import reduce


# COMMAND ----------

# Define the time window: last 3 years from today
end_date = datetime.now()
start_date = end_date - timedelta(days=3*365)

# Read the sales_history table
sales_history = spark.table(f"{catalog}.{schema_silver}.sales_history")

# Filter for last 3 years
sales_history_recent = sales_history.filter(col("week_start").between(start_date, end_date))

# Show a sample
display(sales_history_recent.limit(1000))

# COMMAND ----------

# Find the top 5 (warehouse_id, product_id) pairs with the most records
pair_counts = (sales_history_recent
    .groupBy("warehouse_id", "product_id")
    .count()
    .orderBy(col("count").desc())
)
top_pairs = pair_counts.limit(5).toPandas()
display(top_pairs)

# COMMAND ----------

# Select the top pairs for EDA
selected_pairs = top_pairs[["warehouse_id", "product_id"]].values.tolist()

# Build filter for selected pairs
def filter_for_pairs(df: DataFrame, pairs):
    conditions = [
        (col("warehouse_id") == wid) & (col("product_id") == pid)
        for wid, pid in pairs
    ]
    return df.filter(reduce(lambda a, b: a | b, conditions))

sales_history_selected = filter_for_pairs(sales_history_recent, selected_pairs)
display(sales_history_selected.limit(1000))

# COMMAND ----------

# Find the top 5 (warehouse_id, product_id) pairs with the most records
pair_counts = (sales_history_recent
    .groupBy("warehouse_id", "product_id")
    .count()
    .orderBy(col("count").desc())
)
top_pairs = pair_counts.limit(5).toPandas()
display(top_pairs)

# COMMAND ----------

# Convert the filtered Spark DataFrame to Pandas
pdf_sales_history = sales_history_selected.toPandas()

# Generate the profile report
profile = ydata_profiling.ProfileReport(pdf_sales_history, title="Sales History EDA Report", explorative=True)
profile.to_notebook_iframe()

# COMMAND ----------

# MAGIC %md
# MAGIC %md
# MAGIC ## Step 2: Profile the Data with ydata-profiling
# MAGIC We'll convert the filtered Spark DataFrame to a Pandas DataFrame and use ydata-profiling to generate a profile report. We'll use ydata-profiling version 4.8.3 if needed. Display the profile report for general EDA.

# COMMAND ----------

# Ensure week_start is datetime
pdf_sales_history['week_start'] = pd.to_datetime(pdf_sales_history['week_start'])

# Plot for each selected pair
fig, axes = plt.subplots(len(selected_pairs), 1, figsize=(12, 4 * len(selected_pairs)), sharex=True)
if len(selected_pairs) == 1:
    axes = [axes]
for i, (wid, pid) in enumerate(selected_pairs):
    pair_df = pdf_sales_history[(pdf_sales_history['warehouse_id'] == wid) & (pdf_sales_history['product_id'] == pid)]
    axes[i].plot(pair_df['week_start'], pair_df['weekly_sales'], marker='o')
    axes[i].set_title(f'Warehouse {wid}, Product {pid} - Weekly Sales')
    axes[i].set_ylabel('Weekly Sales')
    axes[i].grid(True)
plt.xlabel('Week Start')
plt.tight_layout()
plt.show()

# COMMAND ----------

# MAGIC %md
# MAGIC %md
# MAGIC ## Step 3: Visualize Weekly Sales Time Series for Selected Pairs
# MAGIC We'll plot weekly sales trends for each of the selected (warehouse_id, product_id) pairs using matplotlib. This will help visually inspect trends, seasonality, and outliers.

# COMMAND ----------

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Ensure week_start is datetime
pdf_sales_history['week_start'] = pd.to_datetime(pdf_sales_history['week_start'])

# Plot for each selected pair
fig, axes = plt.subplots(len(selected_pairs), 1, figsize=(12, 4 * len(selected_pairs)), sharex=True)
if len(selected_pairs) == 1:
    axes = [axes]
for i, (wid, pid) in enumerate(selected_pairs):
    pair_df = pdf_sales_history[(pdf_sales_history['warehouse_id'] == wid) & (pdf_sales_history['product_id'] == pid)]
    axes[i].plot(pair_df['week_start'], pair_df['weekly_sales'], marker='o')
    axes[i].set_title(f'Warehouse {wid}, Product {pid} - Weekly Sales')
    axes[i].set_ylabel('Weekly Sales')
    axes[i].grid(True)
plt.xlabel('Week Start')
plt.tight_layout()
plt.show()