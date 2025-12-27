# /opt/airflow/dags/windows_python_scheduler_final.py
from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.ssh.operators.ssh import SSHOperator

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 1, 1),
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': False,
    'email_on_retry': False,
}

with DAG(
    dag_id='schedule_windows_python_script',
    default_args=default_args,
    description='调度Windows上的Python脚本',
    schedule_interval='@daily',  # 每天执行，可根据需要修改
    catchup=False,
    max_active_runs=1,
    tags=['windows', 'production', 'python']
) as dag:
    
    # 执行您的test.py脚本
    execute_script = SSHOperator(
        task_id='execute_test_py',
        ssh_conn_id='windows_ssh',
        command='cd /d "C:\\Users\\JoeyC\\Desktop\\Find_Job_Pipe_Line_V2" && python dags\\test.py',
        cmd_timeout=600,  # 10分钟超时
        do_xcom_push=True,  # 如果需要捕获输出
        execution_timeout=timedelta(minutes=15),
        retries=2,
        retry_delay=timedelta(minutes=2),
        environment={
            'PYTHONPATH': 'C:\\Users\\JoeyC\\Desktop\\Find_Job_Pipe_Line_V2',
        }
    )
    
    execute_script