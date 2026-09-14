/*
    Control Table: drives the metadata-driven ADF pipeline.
    Each row represents one source table to be ingested.
*/

CREATE TABLE dbo.control_table (
    control_id          INT IDENTITY(1,1) PRIMARY KEY,
    source_schema_name   VARCHAR(100)  NOT NULL,
    source_table_name    VARCHAR(200)  NOT NULL,
    load_type            VARCHAR(20)   NOT NULL,   -- 'APPEND', 'SCD1', 'SCD2', 'FULLLOAD'
    incremental_column    VARCHAR(100)  NULL,       -- e.g. 'ModifiedDate' or 'UpdatedAt'
    last_ingestion_date  DATETIME2     NULL,
    is_active            BIT           NOT NULL DEFAULT 1,
    sink_zone            VARCHAR(20)   NOT NULL DEFAULT 'bronze',
    created_date         DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME(),
    modified_date         DATETIME2     NULL
);

-- Sample rows
INSERT INTO dbo.control_table
    (source_schema_name, source_table_name, load_type, incremental_column, last_ingestion_date, is_active)
VALUES
    ('dbo', 'Customers', 'SCD2',     'ModifiedDate', '2026-01-01', 1),
    ('dbo', 'Orders',    'APPEND',   'CreatedDate',  '2026-01-01', 1),
    ('dbo', 'Products',  'FULLLOAD', NULL,            NULL,         1);

-- Example: stored proc to update last_ingestion_date after a successful load
CREATE PROCEDURE dbo.usp_update_last_ingestion_date
    @control_id INT,
    @ingestion_date DATETIME2
AS
BEGIN
    UPDATE dbo.control_table
    SET last_ingestion_date = @ingestion_date,
        modified_date = SYSUTCDATETIME()
    WHERE control_id = @control_id;
END;
