# %%
import os
import sys
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, TimeoutError as FutureTimeoutError, as_completed

# 获取项目根目录（Lab 的父目录）
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

from Lib.json_yaml_IO import *
from Lib.Html_Analist import HtmlAnalist
from Lib.Batch_Run import BatchRun
from Lib.LLM_Analysis import LLM_model

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


prompts_path = os.path.join(project_root, 'Prompts/company_judgement.yaml')
prompts_config = read_yaml(prompts_path)
prompt = prompts_config.get('Company_score_prompt')

config_path = os.path.join(project_root, 'Lib', 'config_this_before_action.yaml')
config_info = read_yaml(config_path)

llm_model = LLM_model(
    api_key=config_info["your_LLM_api_key"],
    base_url=config_info["your_LLM_base_url"],
    prompts_file=prompts_path
)

# %%
import pandas as pd
import json
def get_company_score(content):
    messages = llm_model.set_messages(
        user_input=content,
        system_prompt=prompt
    )
    result = llm_model.get_json_response(
        messages=messages
    )
    return result


# %%
def bronze_company_judgement():
    df = duckdb_engine.execute_sql_file('read_co_info.sql')
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {}

        # 使用 enumerate 或 iterrows 来获取索引
        for idx, row in df.iterrows():
            # 处理 company_box_content（假设它是一个列表或类似结构）
            if isinstance(row['company_box_content'], list):
                content = [item.strip() if isinstance(item, str) else str(item).strip() for item in row['company_box_content']]
            else:
                # 如果不是列表，尝试转换为列表
                content = [str(row['company_box_content']).strip()]

            future = executor.submit(get_company_score, content)
            futures[future] = idx  # 使用 DataFrame 索引作为 key

        for future in as_completed(futures):
            try:
                result = future.result()
                result = json.loads(result)
                
                # 正确的方式：从字典中提取每个值并赋值
                idx = futures[future]
                df.loc[idx, 'company_size'] = result.get('company_size', 0)
                df.loc[idx, 'ownership'] = result.get('ownership', 0)
                df.loc[idx, 'industry'] = result.get('industry', 0)
                df.loc[idx, 'mentions'] = result.get('mentions', 0)
                df.loc[idx, 'culture'] = result.get('culture', 0)
                df.loc[idx, 'nationality'] = result.get('nationality', 0)

                print(f"Index: {futures[future]}")
                
            except Exception as e:
                print(f"Error at index {futures[future]}: {e}")

    return df



import pyarrow as pa
import pyarrow.parquet as pq
from io import BytesIO

def df_to_parquet(df):
    buffer = BytesIO()
    table = pa.Table.from_pandas(df)
    pq.write_table(table, buffer, compression='snappy')
    buffer.seek(0)
    return buffer.getvalue()


from datetime import datetime

def upload_to_minio(df):
    today = datetime.now().strftime('%Y%m%d')
    buffer_bytes = df_to_parquet(df)
    # Wrap bytes in BytesIO to provide file-like interface
    buffer = BytesIO(buffer_bytes)
    client.put_object(
        bucket_name='jobdatabucket',
        object_name='silver/company_info/dt=' + today + '/company_info_with_score.parquet',
        data=buffer,
        length=len(buffer_bytes)
    )


def main():
    df = bronze_company_judgement()
    upload_to_minio(df)

if __name__ == '__main__':
    main()