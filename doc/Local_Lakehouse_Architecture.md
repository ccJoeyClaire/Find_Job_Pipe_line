# Local Lakehouse Architecture

## Overview

This document defines the architecture and data organization for the local lakehouse built on MinIO + Parquet + DuckDB.

## Architecture Components

```
┌─────────────────┐
│  Data Sources   │
│ (Web/LinkedIn)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Airflow DAGs   │
│  D1, D2, D3...  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│     MinIO        │
│  (Object Store)  │
│                 │
│  ┌───────────┐  │
│  │   raw/    │  │ ← Original HTML/JSON
│  │  staging/ │  │ ← Cleaned Parquet tables
│  │  curated/ │  │ ← Final analytical tables
│  └───────────┘  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    DuckDB        │
│ (Query Engine)   │
└─────────────────┘
```

## Data Zones

The lakehouse uses a **three-zone architecture** within a single MinIO bucket:

### 1. Raw Zone (`raw/`)
- **Purpose**: Store original, unprocessed data
- **Format**: HTML files, JSON files (as-is)
- **Retention**: Long-term (source of truth)
- **Example paths**:
  - `raw/linkedin_html/dt=2024-12-11/job_12345.html`
  - `raw/linkedin_html/dt=2024-12-11/job_67890.html`

### 2. Staging Zone (`staging/`)
- **Purpose**: Store cleaned and normalized structured data
- **Format**: Parquet files (partitioned by date)
- **Retention**: Medium-term (can be reprocessed from raw)
- **Example paths**:
  - `staging/job_table/dt=2024-12-11/jobs.parquet`
  - `staging/company_table/dt=2024-12-11/companies.parquet`
  - `staging/skills_table/dt=2024-12-11/skills.parquet`

### 3. Curated Zone (`curated/`)
- **Purpose**: Store final analytical tables ready for querying
- **Format**: Parquet files (optimized for analytics)
- **Retention**: Long-term (final analytical layer)
- **Example paths**:
  - `curated/job_features/latest.parquet` (or `dt=2024-12-11/job_features.parquet`)
  - `curated/job_company_joined/dt=2024-12-11/job_company.parquet`
  - `curated/cluster_results/dt=2024-12-11/clusters.parquet`

## Bucket Structure

**Main Bucket**: `job-pipeline` (recommended) or keep existing `linkedin-jobs`

### Complete Path Structure

```
job-pipeline/
├── raw/
│   └── linkedin_html/
│       └── dt=YYYY-MM-DD/
│           ├── job_12345.html
│           └── job_67890.html
│
├── staging/
│   ├── job_table/
│   │   └── dt=YYYY-MM-DD/
│   │       └── jobs.parquet
│   ├── company_table/
│   │   └── dt=YYYY-MM-DD/
│   │       └── companies.parquet
│   └── skills_table/
│       └── dt=YYYY-MM-DD/
│           └── skills.parquet
│
└── curated/
    ├── job_features/
    │   └── dt=YYYY-MM-DD/
    │       └── job_features.parquet
    ├── job_company_joined/
    │   └── dt=YYYY-MM-DD/
    │       └── job_company.parquet
    └── cluster_results/
        └── dt=YYYY-MM-DD/
            └── clusters.parquet
```

## Data Flow

### ETL Pipeline Flow

1. **D1_Web_Scrape** (Raw Data Ingestion)
   - Input: Web scraping
   - Output: `raw/linkedin_html/dt={date}/job_{id}.html`

2. **D2_Extra_html_info** (Staging Layer)
   - Input: `raw/linkedin_html/dt={date}/*.html`
   - Processing: HTML parsing, extraction, normalization
   - Output: 
     - `staging/job_table/dt={date}/jobs.parquet`
     - `staging/company_table/dt={date}/companies.parquet`
     - `staging/skills_table/dt={date}/skills.parquet`

3. **D3_Curate_Job_Features** (Curated Layer) - Optional
   - Input: `staging/*/dt={date}/*.parquet`
   - Processing: Feature engineering, joins, aggregations
   - Output: `curated/job_features/dt={date}/job_features.parquet`

### Query Flow

1. **DuckDB** reads Parquet from `curated/` zone
2. Supports SQL queries across multiple Parquet files
3. Can join tables from different zones if needed

## Naming Conventions

### File Naming
- **Raw HTML**: `job_{job_id}.html`
- **Parquet files**: `{table_name}.parquet` (e.g., `jobs.parquet`, `companies.parquet`)
- **Partitioned paths**: `dt=YYYY-MM-DD/` (date partition)

### Table Naming
- **Staging tables**: `{entity}_table` (e.g., `job_table`, `company_table`)
- **Curated tables**: `{purpose}_{entity}` (e.g., `job_features`, `job_company_joined`)

## Configuration

### MinIO Connection
- **Endpoint (from host)**: `http://localhost:9000`
- **Endpoint (from container)**: `http://minio:9000`
- **Console**: `http://localhost:9001`
- **Default credentials**: `minioadmin` / `minioadmin`

### Environment Variables
```bash
MINIO_ENDPOINT=http://minio:9000  # or localhost:9000 from host
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_REGION=us-east-1
MINIO_BUCKET=job-pipeline
```

## Migration from Current Setup

### Current State
- Bucket: `linkedin-jobs`
- Structure: Flat or date-prefixed HTML files
- Example: `job_html_12_05/job_12345.html`

### Target State
- Bucket: `job-pipeline` (or keep `linkedin-jobs`)
- Structure: Three-zone architecture with Parquet in staging/curated

### Migration Strategy
1. Keep existing `linkedin-jobs` bucket for backward compatibility
2. Create new `job-pipeline` bucket for lakehouse structure
3. Gradually migrate new data to new structure
4. Old data can be accessed via `raw/` zone if needed

## Next Steps

1. ✅ Define architecture (this document)
2. ⏳ Standardize MinIO configuration
3. ⏳ Implement Parquet IO utilities
4. ⏳ Add DuckDB query layer
5. ⏳ Update Airflow DAGs to use new structure

