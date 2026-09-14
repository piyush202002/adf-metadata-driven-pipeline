# Architecture Details

## Load Types Supported
| Load Type | Description |
|-----------|-------------|
| Append    | New rows inserted based on incremental column; no updates to existing rows |
| SCD Type 1 | Overwrite existing records with latest values (no history) |
| SCD Type 2 | Maintain historical versions of records with effective/end dates |
| Full Load | Entire source table is truncated and reloaded every run |

## Zones
| Zone   | Description |
|--------|-------------|
| Bronze | Raw data copied as-is from source systems (landing zone) |
| Silver | Cleansed, deduplicated, standardized, and conformed data |
| Gold   | Curated, aggregated data modeled for reporting and analytics consumption |

## Connectivity
- **Self-Hosted Integration Runtime (SHIR)** is installed on a VM within the on-prem network to securely bridge Azure Data Factory with the on-prem SQL Server.
- Linked Services use parameterization so a single Linked Service + Dataset pair can serve all tables listed in the control table.

## Orchestration Flow
1. `Lookup_ControlTable` reads all active source table configs from the control table.
2. `ForEach_SourceTable` iterates over each row returned.
3. Within each iteration:
   - `Copy_OnPremToADLS` copies data from on-prem SQL Server to ADLS Gen2 (Bronze) as Parquet.
   - `Notebook_BronzeToSilverGold` triggers the Databricks notebook to process Bronze → Silver → Gold.
   - `SP_UpdateLastIngestionDate` updates the control table with the latest successful ingestion timestamp.
