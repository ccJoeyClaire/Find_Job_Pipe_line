# /opt/airflow/dags/windows_python_scheduler_final.py
from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.ssh.operators.ssh import SSHOperator # type: ignore

project_root = 'C:\\Users\\JoeyC\\Desktop\\Find_Job_Pipe_Line_V2'
site_packages = 'C:\\ProgramData\\Anaconda3\\Lib\\site-packages'
site_packages_2 = 'C:\\Users\\airflow_worker\\AppData\\Roaming\\Python\\Python312\\site-packages'
script_name = 'test.py'

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 1, 1),
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': False,
    'email_on_retry': False,
}

with DAG(
    dag_id='test_dag',
    default_args=default_args,
    description='调度Windows上的Python脚本',
    schedule_interval=None,  
    catchup=False,
    max_active_runs=1,
    tags=['windows', 'test', 'python']
) as dag:
    
    # 执行您的test.py脚本
    execute_script = SSHOperator(
        task_id='execute_test_py',
        ssh_conn_id='windows_ssh',
        command='cd /d "' + project_root + '" && python dags/' + script_name,
        cmd_timeout=600,  # 10分钟超时
        do_xcom_push=True,  # 如果需要捕获输出
        execution_timeout=timedelta(minutes=15),
        retries=2,
        retry_delay=timedelta(minutes=2),
        environment={
            'PYTHONPATH': project_root + ';' + site_packages + ';' + site_packages_2,
        }
    )
    
    execute_script