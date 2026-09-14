# Metadata-Driven Data Ingestion Pipeline (Azure Data Factory + Databricks)

## 📌 Overview
This project implements a **metadata-driven, dynamic data ingestion framework** using
**Azure Data Factory (ADF)**, **Azure SQL Database**, and **Azure Databricks**.
Instead of building a separate pipeline for every source table, a single generic
pipeline reads configuration from a **control table** and dynamically ingests,
processes, and loads data through a **Bronze → Silver → Gold** medallion architecture.

> **Status:** 🚧 In Progress

---

## 🏗️ Architecture

```
On-Prem SQL Server
        │  (Self-Hosted Integration Runtime)
        ▼
   ADF Copy Activity
        │
        ▼
  ADLS Gen2 (Bronze - Raw)
        │  (Databricks Notebook)
        ▼
  ADLS Gen2 (Silver - Cleansed / Delta)
        │
        ▼
  ADLS Gen2 (Gold - Curated / Business-Ready)
```

Pipeline orchestration flow:

```
Lookup Activity  →  ForEach Activity  →  Copy Activity  →  Notebook Activity  →  Stored Procedure Activity
   (reads               (loops per          (On-Prem SQL         (Bronze → Silver          (post-load
 control table)         source table)      → ADLS Gen2)           → Gold in Databricks)     logging / audit)
```

---

## ⚙️ Components

### 1. Control Table (Azure SQL)
A single metadata table that drives the entire pipeline. Stores:
- Source table name
- Load type: `Append`, `SCD Type 1`, `SCD Type 2`, `Full Load`
- Incremental/watermark column
- Last ingestion date

See [`control-table/control_table_ddl.sql`](control-table/control_table_ddl.sql)

### 2. ADF Pipeline
- **Lookup Activity** — fetches active source table metadata from the control table.
- **ForEach Activity** — iterates over each row (table) returned by the Lookup.
- Inside ForEach:
  - **Copy Activity** — moves data from On-Prem SQL Server → ADLS Gen2 (Bronze).
  - **Notebook Activity** — triggers a Databricks notebook to process Bronze → Silver → Gold.
  - **Stored Procedure Activity** — updates control table (e.g., last ingestion date) / logs run status.

Connectivity:
- **Self-Hosted Integration Runtime (SHIR)** for on-prem SQL Server connectivity.
- Parameterized, query-based **Linked Services** and **Datasets** for both source (SQL Server) and sink (ADLS Gen2).

See [`adf-pipelines/`](adf-pipelines) for linked services, datasets, and pipeline definitions.

### 3. Databricks Notebooks
- Mounts ADLS Gen2 and reads raw data landed by the Copy Activity.
- Builds a DataFrame on raw data and writes it into **Delta tables**.
- Implements the **medallion architecture**:
  | Zone | Purpose |
  |--------|---------|
  | **Bronze** | Raw, unprocessed data as-is from source |
  | **Silver** | Cleansed, validated, and conformed data |
  | **Gold** | Aggregated, business-ready data for reporting/analytics |

See [`databricks-notebooks/`](databricks-notebooks)

---

## 🧱 Tech Stack
- Azure Data Factory
- Azure SQL Database
- Azure Databricks (PySpark, Delta Lake)
- Azure Data Lake Storage Gen2
- Self-Hosted Integration Runtime

---

## 📂 Repository Structure
```
adf-metadata-driven-pipeline/
├── control-table/
│   └── control_table_ddl.sql
├── adf-pipelines/
│   ├── linked-services/
│   ├── datasets/
│   └── pipelines/
├── databricks-notebooks/
│   └── bronze_to_silver_gold.py
├── docs/
│   └── architecture.md
└── README.md
```

---

## 🚀 Future Enhancements
- Add SCD Type 2 handling with surrogate keys and effective date tracking.
- Add data quality checks before Silver/Gold promotion.
- Add pipeline monitoring/alerting (Log Analytics + Azure Monitor).
