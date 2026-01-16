from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.ssh.operators.ssh import SSHOperator # type: ignore

project_root = 'C:\\Users\\JoeyC\\Desktop\\Find_Job_Pipe_Line_V2'
site_packages = 'C:\\ProgramData\\Anaconda3\\Lib\\site-packages'
site_packages_2 = 'C:\\Users\\airflow_worker\\AppData\\Roaming\\Python\\Python312\\site-packages'


r2b_script = 'r2b_processing.py' # from raw to bronze
b2s_script = ['b2s_company_judgement.py', 'b2s_JD_Decompose.py'] # from bronze to silver
s2g_script = ['s2g_get_target_company.py', 's2g_get_target_JD.py'] # from silver to gold



default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 1, 1),
    'retries': 0,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': False,
    'email_on_retry': False,
}

with DAG(
    dag_id='Data_Process_Pipeline',
    default_args=default_args,
    description='从 html 到可投递简历的数据管道',
    schedule_interval=None,  
    catchup=False,
    max_active_runs=1,
    tags=['windows', 'Data_Process_Pipeline', 'python']
) as dag:
    
    # 执行您的raw_processing.py脚本
    r2b_data_process = SSHOperator(
        task_id='r2b_data_process',
        ssh_conn_id='windows_ssh',
        command='cd /d "' + project_root + '" && python dags/' + r2b_script,
        cmd_timeout=600,  # 10分钟超时
        do_xcom_push=True,  # 如果需要捕获输出
        execution_timeout=timedelta(minutes=15),
        retries=0,
        retry_delay=timedelta(minutes=2),
        environment={
            'PYTHONPATH': project_root + ';' + site_packages + ';' + site_packages_2,
        }
    )

    b2s_company_judgement = SSHOperator(
        task_id='b2s_company_judgement',
        ssh_conn_id='windows_ssh',
        command='cd /d "' + project_root + '" && python dags/' + b2s_script[0],
        cmd_timeout=600,  # 10分钟超时
        do_xcom_push=True,  # 如果需要捕获输出
        execution_timeout=timedelta(minutes=15),
        retries=0,
        retry_delay=timedelta(minutes=2),
        environment={
            'PYTHONPATH': project_root + ';' + site_packages + ';' + site_packages_2,
        }
    )


    b2s_JD_Decompose = SSHOperator(
        task_id='b2s_JD_Decompose',
        ssh_conn_id='windows_ssh',
        command='cd /d "' + project_root + '" && python dags/' + b2s_script[1],
        cmd_timeout=600,  # 10分钟超时
        do_xcom_push=True,  # 如果需要捕获输出
        execution_timeout=timedelta(minutes=15),
        retries=0,
        retry_delay=timedelta(minutes=2),
        environment={
            'PYTHONPATH': project_root + ';' + site_packages + ';' + site_packages_2,
        }
    )

    s2g_get_target_company = SSHOperator(
        task_id='s2g_get_target_company',
        ssh_conn_id='windows_ssh',
        command='cd /d "' + project_root + '" && python dags/' + s2g_script[0],
        cmd_timeout=600,  # 10分钟超时
        do_xcom_push=True,  # 如果需要捕获输出
        execution_timeout=timedelta(minutes=15),
        retries=0,
        retry_delay=timedelta(minutes=2),
    )

    s2g_get_target_JD = SSHOperator(
        task_id='s2g_get_target_JD',
        ssh_conn_id='windows_ssh',
        command='cd /d "' + project_root + '" && python dags/' + s2g_script[1],
        cmd_timeout=600,  # 10分钟超时
        do_xcom_push=True,  # 如果需要捕获输出
        execution_timeout=timedelta(minutes=15),
        retries=0,
        retry_delay=timedelta(minutes=2),
    )

    r2b_data_process >> b2s_company_judgement >> b2s_JD_Decompose >> s2g_get_target_company >> s2g_get_target_JD