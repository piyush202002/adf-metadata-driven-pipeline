# Databricks notebook: Bronze -> Silver -> Gold
# Triggered by ADF Notebook Activity with parameters: table_name, load_type

# COMMAND ----------
dbutils.widgets.text("table_name", "")
dbutils.widgets.text("load_type", "APPEND")

table_name = dbutils.widgets.get("table_name")
load_type = dbutils.widgets.get("load_type")

# COMMAND ----------
# Mount / access ADLS Gen2 (example using abfss direct access)
raw_path = f"abfss://raw@<storageaccountname>.dfs.core.windows.net/bronze/{table_name}"
bronze_delta_path = f"abfss://bronze@<storageaccountname>.dfs.core.windows.net/{table_name}"
silver_delta_path = f"abfss://silver@<storageaccountname>.dfs.core.windows.net/{table_name}"
gold_delta_path = f"abfss://gold@<storageaccountname>.dfs.core.windows.net/{table_name}"

# COMMAND ----------
# --- Bronze: land raw data as Delta ---
df_raw = spark.read.parquet(raw_path)
df_raw.write.format("delta").mode("append").save(bronze_delta_path)

# COMMAND ----------
# --- Silver: cleanse & conform ---
df_bronze = spark.read.format("delta").load(bronze_delta_path)

df_silver = (
    df_bronze
    .dropDuplicates()
    .na.drop(how="all")
    # add column standardization / type casting / dedup logic per load_type (APPEND / SCD1 / SCD2 / FULLLOAD)
)

df_silver.write.format("delta").mode("overwrite").save(silver_delta_path)

# COMMAND ----------
# --- Gold: business-ready aggregation ---
df_gold = spark.read.format("delta").load(silver_delta_path)
# TODO: apply business transformations / aggregations specific to this table
df_gold.write.format("delta").mode("overwrite").save(gold_delta_path)

# COMMAND ----------
print(f"Completed Bronze -> Silver -> Gold load for table: {table_name}")
