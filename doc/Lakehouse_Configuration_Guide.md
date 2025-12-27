# Lakehouse Configuration Guide

## Environment Variables

Create a `.env` file in the `WorkFlow/` directory with the following variables:

```bash
# MinIO Configuration
# Use 'minio:9000' when running inside Docker containers
# Use 'localhost:9000' when running from host machine
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_REGION=us-east-1

# Lakehouse Bucket Configuration
MINIO_BUCKET=job-pipeline

# Airflow Configuration (if needed)
AIRFLOW_UID=50000
_AIRFLOW_WWW_USER_USERNAME=airflow
_AIRFLOW_WWW_USER_PASSWORD=airflow

# MinIO Ports (for docker-compose)
MINIO_API_PORT=9000
MINIO_CONSOLE_PORT=9001
```

## Configuration by Environment

### From Docker Containers (Airflow DAGs)
- **MINIO_ENDPOINT**: `http://minio:9000` (use service name)
- **MINIO_ACCESS_KEY**: `minioadmin` (default)
- **MINIO_SECRET_KEY**: `minioadmin` (default)

### From Host Machine (Local Python Scripts)
- **MINIO_ENDPOINT**: `localhost:9000` (use localhost)
- **MINIO_ACCESS_KEY**: `minioadmin` (default)
- **MINIO_SECRET_KEY**: `minioadmin` (default)

## Usage in Code

### Using Environment Variables

```python
import os
from Lib.minio_storage import create_minio_storage

# Automatically reads from environment variables
storage = create_minio_storage(
    bucket_name=os.getenv('MINIO_BUCKET', 'job-pipeline')
)
```

### Manual Configuration

```python
from Lib.minio_storage import MinIOStorage

storage = MinIOStorage(
    endpoint="minio:9000",  # or "localhost:9000"
    access_key="minioadmin",
    secret_key="minioadmin",
    bucket_name="job-pipeline"
)
```

## Zone Path Helpers

Use the lakehouse zone helpers from `minio_storage.py`:

```python
from Lib.minio_storage import get_lakehouse_path

# Raw zone
raw_path = get_lakehouse_path("raw", "linkedin_html", "2024-12-11", "job_12345.html")
# Returns: "raw/linkedin_html/dt=2024-12-11/job_12345.html"

# Staging zone
staging_path = get_lakehouse_path("staging", "job_table", "2024-12-11", "jobs.parquet")
# Returns: "staging/job_table/dt=2024-12-11/jobs.parquet"

# Curated zone
curated_path = get_lakehouse_path("curated", "job_features", "2024-12-11", "job_features.parquet")
# Returns: "curated/job_features/dt=2024-12-11/job_features.parquet"
```

