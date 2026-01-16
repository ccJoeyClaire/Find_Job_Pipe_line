import os
import sys

# Fix encoding issues on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

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

from Lib.json_yaml_IO import *
from Lib.Html_Analist import HtmlAnalist
from Lib.Batch_Run import BatchRun

from minio import Minio
from minio.error import S3Error

client = Minio(
    endpoint="localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)

import threading
import time
import logging
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, TimeoutError as FutureTimeoutError, as_completed
from typing import Callable, List, Any, Optional, Tuple, Dict, Iterable, Union
from dataclasses import dataclass
from enum import Enum

def safe_print(*args, **kwargs):
    """Print function that handles encoding errors gracefully."""
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        # If encoding fails, encode with error handling
        message = ' '.join(str(arg) for arg in args)
        try:
            print(message.encode('utf-8', errors='replace').decode('utf-8'), **kwargs)
        except:
            print(message.encode('ascii', errors='replace').decode('ascii'), **kwargs)

def read_from_s3(bucket_name, object_name):
    response = client.get_object(bucket_name, object_name)
    content = response.read()
    response.close()
    return content


def extract_location_and_time(text):
    import re
    try:
        # 北上广深直接返回
        if '北京' in text:
            location = '北京'
        elif '上海' in text:
            location = '上海'
        elif '广州' in text:
            location = '广州'
        elif '深圳' in text:
            location = '深圳'
        else:
            # 其他省份
            provinces = ['河北', '山西', '辽宁', '吉林', '黑龙江', '江苏', '浙江', 
                        '安徽', '福建', '江西', '山东', '河南', '湖北', '湖南', 
                        '广东', '海南', '四川', '贵州', '云南', '陕西', '甘肃', 
                        '青海', '内蒙古', '广西', '西藏', '宁夏', '新疆']
        
            for province in provinces:
                if province in text:
                    location = province
            if not location:
                location = None
        
        time_pattern = re.compile(r'(?<!\d)(?:(?:\d{1,4}\s*(?:分钟|小时|天|周|个月|年))|(?:今天|昨天|前天)\s*\d{1,2}:\d{2})|(?:\d{1,2}\s*秒前)')
        time_match = time_pattern.search(text)
        if time_match:
            time = time_match.group(0)
        else:
            time = None
    except Exception as e:
        safe_print(f"Error extracting location and time: {e}")
        location = None
        time = None

    return location, time



def process_file(content: bytes) -> Any:
    html_processor = HtmlAnalist(content)

    company_url_and_name = html_processor.get_company_url_and_name()
    company_url = company_url_and_name['company_url']
    company_name = company_url_and_name['company_name']

    info = html_processor.info
    location, time = extract_location_and_time(info)

    result = {
        'job_name': html_processor.head,
        'job_url': html_processor.head_url,
        'company_name': company_name,
        'company_url': company_url,
        'location': location,
        'time': time,
        'job_details_content': html_processor.get_job_details_content(),
        'company_box_content': html_processor.get_company_box_content()
    }

    safe_print(f'Processing: {result["company_name"]} - {result["job_name"]}')
    return result

def save_json_to_s3(
    processed_content, bucket_name, object_path, content_name):

    from io import BytesIO
    import json

    
    data = json.dumps(processed_content, indent=4).encode('utf-8')
    data_stream = BytesIO(data)

    try:
        client.put_object(
            bucket_name=bucket_name, 
            object_name=f'{object_path}/{content_name}', 
            data=data_stream,
            length=len(data),
            content_type='application/json'
        )
    except Exception as e:
        safe_print(f"Error saving json to s3: {e}")



def main():
    from datetime import datetime
    today = datetime.now().strftime('%Y%m%d')

    bucket_name = "jobdatabucket"
    html_dir = f"raw/Linkedin_html/dt={today}"

    contents = []
    objects = client.list_objects(bucket_name, prefix=html_dir, recursive=True)

    start_time = time.time()
    # 处理完成的任务
    completed_count = 0
    with ThreadPoolExecutor(max_workers=15) as executor:
        futures = []
        # 提交所有任务
        for obj in objects:
            future = executor.submit(read_from_s3, bucket_name, obj.object_name)
            futures.append(future)
            
        for future in as_completed(futures):
            try:
                content = future.result()
            except Exception as e:
                safe_print(f"Error processing: {e}")
                
            contents.append(content)
            completed_count += 1

            print(f"\rProgress: {completed_count}", end="", flush=True)
            print(f"Time taken: {time.time() - start_time:.2f} seconds")

    processed_contents = []
    for raw_content in contents:
        processed_content = process_file(raw_content)
        processed_contents.append(processed_content)
    
    
    object_path = f"bronze/raw_json/dt={today}"
    for processed_content in processed_contents:
        content_name = f'{processed_content['company_name']}_{processed_content['job_name']}.json'
        save_json_to_s3(processed_content, bucket_name, object_path, content_name)


if __name__ == "__main__":
    main()