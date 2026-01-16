import os
import sys

# Get project root directory (parent of Lab)
current_dir = os.getcwd()
if current_dir.endswith('Find_Job_Pipe_Line_V2'):
    project_root = current_dir
else:
    project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)
lib_path = os.path.join(project_root, 'Lib')
sys.path.insert(0, lib_path)

print(f"项目根目录: {project_root}")
print(f"Lib 目录存在: {os.path.exists(os.path.join(project_root, 'Lib'))}")


from minio import Minio
from minio.error import S3Error

client = Minio(
    endpoint="localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)


from Lib.exe_SQL import Exe_SQL
import pandas as pd
import numpy as np

duckdb_engine = Exe_SQL()
duckdb_engine.connect()


import pyarrow as pa
import pyarrow.parquet as pq
from datetime import datetime
from io import BytesIO

def df_to_parquet(df):
    buffer = BytesIO()
    table = pa.Table.from_pandas(df)
    pq.write_table(table, buffer)
    buffer.seek(0)
    return buffer.getvalue()

def upload_to_minio(df):
    today = datetime.now().strftime('%Y%m%d')
    buffer_bytes = df_to_parquet(df)
    # Wrap bytes in BytesIO to provide file-like interface
    buffer = BytesIO(buffer_bytes)
    client.put_object(
        bucket_name='jobdatabucket',
        object_name='gold/target_company/dt=' + today + '/target_company.parquet',
        data=buffer,
        length=len(buffer_bytes)
    )


def main():

    df = duckdb_engine.execute_sql_file('read_target_company.sql')
    upload_to_minio(df)

if __name__ == "__main__":
    main()