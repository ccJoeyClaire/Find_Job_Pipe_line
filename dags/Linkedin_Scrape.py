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
# %%
from Lib.get_Linkedin import linkedin_job_scraper
# %%
from datetime import datetime
import time
import io

from minio import Minio
from minio.error import S3Error

client = Minio(
    endpoint="localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)

def html_to_bytes(html_content):
    return html_content.encode('utf-8')

def up_load_to_minio(file_bytes, bucket_name, object_name):
    # 将 bytes 对象转换为 BytesIO 对象（文件对象）
    data_stream = io.BytesIO(file_bytes)
    client.put_object(
        bucket_name=bucket_name,
        object_name=object_name,
        data=data_stream,
        length=len(file_bytes)
    )

if __name__ == "__main__":
    today = datetime.now().strftime('%Y%m%d')
    scraper = linkedin_job_scraper()
    scraper.get_url(target_url=scraper.base_url)
    time.sleep(10)
    scraper.login()
    if scraper.check_login_success():
        print("Login successful")
    else:
        print("Login failed")
    
    bucket_name = "jobdatabucket"

    job_details_set = scraper.get_all_job_details(page_num=2)
    for job_id, job_details_soup in job_details_set.items():
        object_name = f"raw/Linkedin_html/dt={today}/{job_id}.html"
        file_bytes = html_to_bytes(job_details_soup.prettify())
        up_load_to_minio(file_bytes, bucket_name, object_name)