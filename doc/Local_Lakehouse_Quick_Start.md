# Local Lakehouse Quick Start Guide

## Overview

This guide helps you get started with the local lakehouse setup (MinIO + Parquet + DuckDB).

## Prerequisites

1. **Docker and Docker Compose** installed
2. **Python 3.8+** with required packages
3. **Local HTML files** in `Lib/job_html_12_10/` directory

## Step 1: Start MinIO

```bash
cd WorkFlow
docker compose up -d minio
```

Verify MinIO is running:
- **Console**: http://localhost:9001 (login: minioadmin/minioadmin)
- **API**: http://localhost:9000

## Step 2: Install Python Dependencies

```bash
pip install -r WorkFlow/requirements.txt
```

Key packages:
- `duckdb>=0.9.0`
- `pandas>=2.0.0`
- `pyarrow>=14.0.0`
- `minio>=7.2.0`

## Step 3: Process HTML Files to Lakehouse

### Option A: Using Airflow DAG (Recommended)

1. **Start Airflow**:
   ```bash
   cd WorkFlow
   docker compose up -d
   ```

2. **Access Airflow UI**: http://localhost:8080
   - Username: `airflow`
   - Password: `airflow`

3. **Trigger DAG**: `D2_Process_HTML_to_Lakehouse`
   - This DAG will:
     - Read HTML files from `Lib/job_html_12_10/`
     - Save raw HTML to `raw/linkedin_html/dt={date}/`
     - Parse HTML and save structured data to `staging/job_table/dt={date}/jobs.parquet`

### Option B: Manual Python Script

```python
from Lib.parquet_io import save_dataframe_to_minio
from Lib.minio_storage import create_minio_storage, get_lakehouse_path
from Lib.Html_Analist import HtmlAnalist
import pandas as pd
import os

# Configuration
local_html_dir = "Lib/job_html_12_10"
run_date = "2024-12-11"
storage = create_minio_storage()

# Process HTML files
parsed_data = []
for html_file in os.listdir(local_html_dir):
    if html_file.endswith('.html'):
        html_path = os.path.join(local_html_dir, html_file)
        job_id = html_file.replace('.html', '')
        
        # Parse HTML
        html_analist = HtmlAnalist(html_path)
        result = html_analist.user_input_for_LLM()
        result['job_id'] = job_id
        result['processed_date'] = run_date
        parsed_data.append(result)

# Save to staging
df = pd.DataFrame(parsed_data)
save_dataframe_to_minio(
    df=df,
    zone="staging",
    table_name="job_table",
    date=run_date,
    filename="jobs.parquet",
    storage=storage
)
```

## Step 4: Query Data with DuckDB

### Method 1: Direct DataFrame Loading

```python
from Lib.parquet_io import load_dataframe_from_minio

df = load_dataframe_from_minio(
    zone="staging",
    table_name="job_table",
    date="2024-12-11",
    filename="jobs.parquet"
)

print(df.head())
```

### Method 2: DuckDB SQL Queries

```python
from Lib.duckdb_client import create_duckdb_client

with create_duckdb_client() as client:
    df = client.query_parquet_file(
        zone="staging",
        table_name="job_table",
        date="2024-12-11",
        filename="jobs.parquet",
        sql_query="""
        SELECT 
            job_id,
            head as job_title,
            head_url
        FROM parquet_file
        WHERE head LIKE '%Engineer%'
        LIMIT 10
        """
    )
    print(df)
```

### Method 3: Register Table for Multiple Queries

```python
from Lib.duckdb_client import create_duckdb_client

with create_duckdb_client() as client:
    # Register table
    client.register_parquet_table(
        table_name="jobs",
        zone="staging",
        table_name_path="job_table",
        date="2024-12-11",
        filename="jobs.parquet"
    )
    
    # Run multiple queries
    df_count = client.query_sql("SELECT COUNT(*) FROM jobs")
    df_titles = client.query_sql("SELECT DISTINCT head FROM jobs LIMIT 10")
    
    print(df_count)
    print(df_titles)
```

## Step 5: Explore with Notebook

Open `Lib/lakehouse_analysis_example.ipynb` for comprehensive examples.

## Data Structure

After processing, your MinIO bucket will have:

```
job-pipeline/
├── raw/
│   └── linkedin_html/
│       └── dt=2024-12-11/
│           ├── 4053052653.html
│           ├── 4102330174.html
│           └── ...
│
└── staging/
    └── job_table/
        └── dt=2024-12-11/
            └── jobs.parquet
```

## Troubleshooting

### MinIO Connection Issues

- **From host**: Use `localhost:9000`
- **From Docker container**: Use `minio:9000`
- Check network: `docker network ls` and ensure containers are on `app-network`

### Data Not Found

- Verify DAG execution succeeded
- Check MinIO console: http://localhost:9001
- Verify bucket name matches: `job-pipeline` (or check `MINIO_BUCKET` env var)

### Import Errors

- Ensure `Lib/` directory is in Python path
- In Airflow: Already configured via volume mount
- Locally: Add to `sys.path` or use relative imports

## Next Steps

1. **Create curated tables**: Add feature engineering DAG
2. **Set up partitioning**: Partition by date/category for better performance
3. **Add metadata tracking**: Track schema versions and data lineage
4. **Integrate with BI tools**: Connect DuckDB to visualization tools

## Reference Documents

- `Local_Lakehouse_Architecture.md` - Architecture details
- `Lakehouse_Configuration_Guide.md` - Configuration options
- `Local_Lakehouse_PySpark_Design.md` - PySpark integration (future)

