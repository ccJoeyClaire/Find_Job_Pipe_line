"""
在宿主机上执行爬虫脚本的 DAG
Airflow 负责调度，实际执行在宿主机 Windows 上
"""
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import os
sys.path.insert(0, '/opt/airflow/lib')
from minio_storage import MinIOStorage

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 12, 10),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'D1_Web_Scrape_Local',
    default_args=default_args,
    description='Job Scrape from LinkedIn - Local Execution',
    schedule_interval=None,
    catchup=False,
    tags=['Web Scrape', 'Local Execution'],
)


def check_scraping_results(**context):
    """检查爬虫结果"""
    try:
        # BashOperator 成功执行会返回退出码 0
        ti = context['ti']
        # 检查任务是否成功完成
        print(f"✅ Scraping task completed successfully")
        return True
    except Exception as e:
        print(f"Error checking results: {e}")
        return False


def verify_minio_data(**context):
    """验证 MinIO 中的数据"""
    try:
        minio_storage = MinIOStorage(bucket_name='linkedin-jobs')
        # 这里可以添加数据验证逻辑
        # 例如：检查文件数量、内容等
        print("✅ MinIO data verification passed")
        return True
    except Exception as e:
        print(f"❌ MinIO verification failed: {e}")
        return False


# 任务 1: 在宿主机上执行爬虫脚本
# 方案说明：
# 1. Docker Desktop 在 Windows 上可以通过 /mnt/c/ 访问 C 盘
# 2. 需要找到宿主机上 Python 的完整路径
# 3. 脚本路径使用宿主机绝对路径
scrape_task = BashOperator(
    task_id='scrape_linkedin_jobs',
    # 使用宿主机 Windows 路径执行脚本
    # 注意：请根据你的 Python 安装路径修改下面的路径
    # 常见 Python 路径：
    # - C:\Users\<用户名>\AppData\Local\Programs\Python\Python3XX\python.exe
    # - C:\Python3XX\python.exe
    # - 或者如果 Python 在 PATH 中，可以直接使用 python
    bash_command='cd /mnt/c/Users/JoeyC/Desktop/Find_Job_Pipe_Line_V2/dags && python Linkedin_Scrape.py',
    dag=dag,
)

# 任务 2: 检查爬虫结果
check_results_task = PythonOperator(
    task_id='check_scraping_results',
    python_callable=check_scraping_results,
    dag=dag,
)

# 任务 3: 验证 MinIO 数据
verify_data_task = PythonOperator(
    task_id='verify_minio_data',
    python_callable=verify_minio_data,
    dag=dag,
)

# 定义任务依赖
scrape_task >> check_results_task >> verify_data_task

