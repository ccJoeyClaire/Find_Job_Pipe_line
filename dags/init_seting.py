from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.ssh.operators.ssh import SSHOperator
from airflow.models import Variable

# 获取项目根目录路径（可以通过 Airflow Variable 配置，或使用默认值）
try:
    PROJECT_ROOT = Variable.get('project_root')
except:
    PROJECT_ROOT = 'C:\\Users\\JoeyC\\Desktop\\Find_Job_Pipe_Line_V2'

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 1, 1),
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': False,
    'email_on_retry': False,
}

with DAG(
    dag_id='init_setting',
    default_args=default_args,
    description='初始化DAG - 可执行dags文件夹下的任何Python脚本',
    schedule_interval=None,  # 手动触发，不自动调度
    catchup=False,
    max_active_runs=1,
    tags=['windows', 'init', 'python'],
    params={
        'script_name': 'test.py',  # 默认执行的脚本，可通过DAG运行配置覆盖
    }
) as dag:
    
    # 执行dags文件夹下的Python脚本
    # 使用Jinja2模板动态获取脚本名称：
    # 1. 优先从 dag_run.conf 获取（手动触发时传入的配置）
    # 2. 如果没有，则从 params 获取（默认值）
    # 
    # 使用方法：
    # - 默认执行：直接触发DAG，会执行 test.py
    # - 指定脚本：在触发DAG时，在"Configuration JSON"中输入：{"script_name": "Linkedin_Scrape.py"}
    execute_script = SSHOperator(
        task_id='execute_python_script',
        ssh_conn_id='windows_ssh',
        command='cd /d "' + PROJECT_ROOT + '" && python dags\\{{ (dag_run.conf.get("script_name") or params.script_name) }}',
        cmd_timeout=600,  # 10分钟超时
        do_xcom_push=True,  # 如果需要捕获输出
        execution_timeout=timedelta(minutes=15),
        retries=2,
        retry_delay=timedelta(minutes=2),
        environment={
            'PYTHONPATH': PROJECT_ROOT,
        }
    )
    
    execute_script