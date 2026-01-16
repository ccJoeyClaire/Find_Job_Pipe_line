# %%
import os
import sys

# 获取项目根目录（Lab 的父目录）
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


from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, TimeoutError as FutureTimeoutError, as_completed

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


def clean_content(content):
    content = content.replace('职位简介', '')
    content = content.replace('职位描述', '')
    content = content.replace('职位福利', '')
    content = content.replace('此职位来源自其他求职网站', '')
    content = content.replace('了解更多', '')
    content = content.replace('该职位来源于猎聘', '')
    content = content.replace('职责描述', '')
    content = content.replace(';;', '')
    content = content.replace('。;', '')
    content = content.replace(';。', '')
    return content


prompts_path = os.path.join(project_root, 'Prompts', 'JD_judgement.yaml')
prompts = read_yaml(prompts_path)
prompt = prompts.get("JD_Decompose_prompt")


llm_model = LLM_model(
    api_key="sk-826ec0296c7e4098b3e50b1588d11a5b",
    base_url="https://api.deepseek.com",
    prompts_file=prompts_path
)

import json
def get_JD_decompose(content):
    messages = llm_model.set_messages(
        user_input=content,
        system_prompt=prompt
    )
    result = llm_model.get_json_response(
        messages=messages)

    return result


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
        object_name='silver/JD_Processed/dt=' + today + '/JD_Processed.parquet',
        data=buffer,
        length=len(buffer_bytes)
    )

# %%
def main():
    df = duckdb_engine.execute_sql_file('read_JD.sql')
    # %%
    JD_processed = pd.DataFrame()
    with ThreadPoolExecutor(max_workers=16) as executor:
        futures = {}

        for idx, row in df.iterrows():
            content = row['job_details_content']
            content = clean_content(content)
            future = executor.submit(get_JD_decompose, content)
            futures[future] = idx

        for future in as_completed(futures):
            try:
                result = future.result()
                result = json.loads(result)
                
                idx = futures[future]
                row = df.loc[idx]

                # 使用字典一次性创建行数据，避免逐个赋值的问题
                row_data = {
                    'job_name': row['job_name'],
                    'company_name': row['company_name'],
                    'one_sentence_description': result.get('one_sentence_description', ''),
                    'keywords': result.get('keywords', []),  # 直接存储 list，Parquet 支持
                    'edu_requirement': result.get('edu_requirement', ''),
                    'work_exp_requirement': result.get('work_exp_requirement', ''),
                    'job_details_content': row['job_details_content']
                }
                
                JD_processed = pd.concat([JD_processed, pd.DataFrame([row_data], index=[idx])], ignore_index=False)

                print(f"Index: {idx}")

            except Exception as e:
                print(f"Error at index {futures[future]}: {e}")

    upload_to_minio(JD_processed)




if __name__ == '__main__':
    main()