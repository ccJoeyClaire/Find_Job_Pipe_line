from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.ssh.operators.ssh import SSHOperator # type: ignore
from airflow.models import Variable



project_root = 'C:\\Users\\JoeyC\\Desktop\\Find_Job_Pipe_Line_V2'
site_packages = 'C:\\ProgramData\\Anaconda3\\Lib\\site-packages'
site_packages_2 = 'C:\\Users\\airflow_worker\\AppData\\Roaming\\Python\\Python312\\site-packages'

def create_dag(dag_id: str, tags: list[str]):
    default_args = {
        'owner': 'airflow',
        'start_date': datetime(2024, 1, 1),
        'retries': 2,
        'retry_delay': timedelta(minutes=5),
        'email_on_failure': False,
        'email_on_retry': False,
    }

    dag = DAG(
        dag_id=dag_id,
        default_args=default_args,
        description='调度Windows上的Python脚本',
        schedule_interval=None,  
        catchup=False,
        max_active_runs=1,
        tags=tags
    )

    return dag

def create_ssh_task(task_id: str, script_name: str, dag: DAG):
    """创建 SSH 执行任务"""
    return SSHOperator(
        task_id=task_id,
        ssh_conn_id='windows_ssh',
        command='cd /d "' + project_root + '" && python dags/' + script_name,
        cmd_timeout=600,  # 10分钟超时
        do_xcom_push=True,  # 如果需要捕获输出
        execution_timeout=timedelta(minutes=15),
        retries=2,
        retry_delay=timedelta(minutes=2),
        environment={
            'PYTHONPATH': project_root + ';' + site_packages + ';' + site_packages_2,
        },
        dag=dag
    )

def create_dag_with_task(dag_id: str, script_name: str, tags: list[str]):
    """创建包含任务的 DAG"""
    dag = create_dag(dag_id, tags)
    
    # 在 DAG 上下文中创建任务
    with dag:
        execute_script = create_ssh_task(
            task_id=f'execute_{script_name.replace(".py", "")}',
            script_name=script_name,
            dag=dag
        )
    
    return dag

def create_dag_with_dependencies(dag_id: str, script_names: list[str], tags: list[str]):
    """创建包含多个任务和依赖关系的 DAG
    
    示例：
    - script_names = ['script1.py', 'script2.py', 'script3.py']
    - 依赖关系：script1 -> script2 -> script3
    """
    dag = create_dag(dag_id, tags)
    
    # 创建多个任务
    tasks = []
    with dag:
        for script_name in script_names:
            task = create_ssh_task(
                task_id=f'execute_{script_name.replace(".py", "")}',
                script_name=script_name,
                dag=dag
            )
            tasks.append(task)
        
        # 方法1：使用 >> 操作符设置依赖（推荐）
        # task1 >> task2 >> task3 表示 task1 先执行，然后 task2，最后 task3
        if len(tasks) > 1:
            for i in range(len(tasks) - 1):
                tasks[i] >> tasks[i + 1]
        
        # 方法2：使用 set_downstream() 方法（等价于上面的 >>）
        # tasks[0].set_downstream(tasks[1])
        # tasks[1].set_downstream(tasks[2])
        
        # 方法3：使用 set_upstream() 方法（与 set_downstream 相反）
        # tasks[1].set_upstream(tasks[0])
        # tasks[2].set_upstream(tasks[1])
        
        # 方法4：并行执行多个任务后执行下一个任务
        # task1 >> [task2, task3] >> task4  # task2 和 task3 并行执行，都完成后执行 task4
    
    return dag

# 在模块顶层创建 DAG，Airflow 才能识别

# 示例1：单个任务
# script_name = 'test.py'
# dag_id = 'test_dag'
# tags = ['windows', 'test', 'python']
# dag = create_dag_with_task(dag_id, script_name, tags)

# 示例2：多个任务，顺序执行（有依赖关系）
script_names = ['test.py', 'raw_processing.py']  # test.py 先执行，然后 raw_processing.py
dag_id = 'test_dag_with_dependencies'
tags = ['windows', 'test', 'python', 'dependencies']
dag = create_dag_with_dependencies(dag_id, script_names, tags)