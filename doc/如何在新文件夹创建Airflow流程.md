# 如何在新文件夹创建 Airflow 流程

本指南详细说明如何从零开始在一个新文件夹中创建和配置 Airflow 工作流。

## 前置要求

1. **已安装 Docker Desktop for Windows**
   - 下载地址：https://www.docker.com/products/docker-desktop
   - 确保 Docker Desktop 正在运行

2. **验证 Docker 可用**
   ```powershell
   docker --version
   docker compose version
   ```

## 步骤 1: 创建项目目录结构

### 1.1 创建项目根目录

```powershell
# 创建新项目目录（例如：my_airflow_project）
New-Item -ItemType Directory -Path "C:\Users\JoeyC\my_airflow_project"
cd C:\Users\JoeyC\my_airflow_project
```

### 1.2 创建必要的子目录

```powershell
# 创建 DAG 目录
New-Item -ItemType Directory -Path "dags"

# 创建日志目录
New-Item -ItemType Directory -Path "logs"

# 创建插件目录（可选）
New-Item -ItemType Directory -Path "plugins"

# 创建数据目录（用于存放输入输出文件）
New-Item -ItemType Directory -Path "data"
```

**最终目录结构**:
```
my_airflow_project/
├── dags/           # DAG 文件目录
├── logs/           # 日志目录
├── plugins/        # 插件目录（可选）
├── data/           # 数据目录
└── docker-compose.yml  # Docker Compose 配置文件
```

## 步骤 2: 创建 docker-compose.yml 文件

### 2.1 复制现有配置

**方法 1: 从现有项目复制**

```powershell
# 从现有项目复制 docker-compose.yml
Copy-Item "C:\Users\JoeyC\airflow\docker-compose.yml" -Destination "C:\Users\JoeyC\my_airflow_project\docker-compose.yml"
```

**方法 2: 手动创建**

在项目根目录创建 `docker-compose.yml` 文件，内容如下：

```yaml
version: '3.8'

x-airflow-common:
  &airflow-common
  image: apache/airflow:2.8.0
  environment:
    &airflow-common-env
    AIRFLOW__CORE__EXECUTOR: LocalExecutor
    AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres/airflow
    AIRFLOW__CORE__FERNET_KEY: ''
    AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION: 'true'
    AIRFLOW__CORE__LOAD_EXAMPLES: 'false'
    AIRFLOW__API__AUTH_BACKENDS: 'airflow.api.auth.backend.basic_auth,airflow.api.auth.backend.session'
    AIRFLOW__SCHEDULER__ENABLE_HEALTH_CHECK: 'true'
  volumes:
    - ./dags:/opt/airflow/dags
    - ./logs:/opt/airflow/logs
    - ./plugins:/opt/airflow/plugins
    - ./data:/opt/airflow/data
  user: "${AIRFLOW_UID:-50000}:0"
  depends_on:
    &airflow-common-depends-on
    postgres:
      condition: service_healthy

services:
  postgres:
    image: postgres:13
    environment:
      POSTGRES_USER: airflow
      POSTGRES_PASSWORD: airflow
      POSTGRES_DB: airflow
    volumes:
      - postgres-db-volume:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "airflow"]
      interval: 10s
      retries: 5
      start_period: 5s
    restart: always

  airflow-webserver:
    <<: *airflow-common
    command: webserver
    ports:
      - "8080:8080"
    healthcheck:
      test: ["CMD", "curl", "--fail", "http://localhost:8080/health"]
      interval: 10s
      timeout: 10s
      retries: 5
      start_period: 30s
    restart: always
    depends_on:
      <<: *airflow-common-depends-on
      airflow-init:
        condition: service_completed_successfully

  airflow-scheduler:
    <<: *airflow-common
    command: scheduler
    healthcheck:
      test: ["CMD-SHELL", 'airflow jobs check --job-type SchedulerJob --hostname "$${HOSTNAME}"']
      interval: 10s
      timeout: 10s
      retries: 5
      start_period: 30s
    restart: always
    depends_on:
      <<: *airflow-common-depends-on
      airflow-init:
        condition: service_completed_successfully

  airflow-init:
    <<: *airflow-common
    entrypoint: /bin/bash
    command:
      - -c
      - |
        echo "Initializing Airflow..."
        if [[ -z "$${AIRFLOW_UID}" ]]; then
          echo "WARNING: AIRFLOW_UID not set, using default 50000"
        fi
        mkdir -p /sources/logs /sources/dags /sources/plugins
        chown -R "$${AIRFLOW_UID:-50000}:0" /sources/{logs,dags,plugins} 2>/dev/null || true
        exec /entrypoint airflow version
    environment:
      <<: *airflow-common-env
      _AIRFLOW_DB_MIGRATE: 'true'
      _AIRFLOW_WWW_USER_CREATE: 'true'
      _AIRFLOW_WWW_USER_USERNAME: ${_AIRFLOW_WWW_USER_USERNAME:-airflow}
      _AIRFLOW_WWW_USER_PASSWORD: ${_AIRFLOW_WWW_USER_PASSWORD:-airflow}
    user: "0:0"
    volumes:
      - ${AIRFLOW_PROJ_DIR:-.}:/sources

volumes:
  postgres-db-volume:
```

### 2.2 自定义配置（可选）

#### 修改端口（如果 8080 被占用）

```yaml
airflow-webserver:
  ports:
    - "8081:8080"  # 改为 8081，访问时使用 http://localhost:8081
```

#### 修改数据库密码（生产环境推荐）

```yaml
postgres:
  environment:
    POSTGRES_PASSWORD: your-secure-password  # 修改密码

# 同时更新 Airflow 连接字符串
AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:your-secure-password@postgres/airflow
```

#### 修改数据目录路径

如果需要使用不同的数据目录：

```yaml
volumes:
  - ./my-data:/opt/airflow/data  # 修改为 my-data
```

## 步骤 3: 初始化 Airflow

### 3.1 首次初始化

```powershell
# 确保在项目根目录
cd C:\Users\JoeyC\my_airflow_project

# 初始化 Airflow（创建数据库、创建管理员用户等）
docker compose up airflow-init
```

**这个过程会**:
- 下载 Docker 镜像（首次运行，可能需要几分钟）
- 创建 PostgreSQL 数据库
- 执行数据库迁移（创建表结构）
- 创建默认管理员用户（用户名: `airflow`，密码: `airflow`）

**成功标志**:
```
airflow-init exited with code 0
```

### 3.2 验证初始化

```powershell
# 检查初始化是否成功
docker compose ps
```

应该看到 `airflow-init` 的状态为 `Exited (0)`。

## 步骤 4: 创建你的第一个 DAG

### 4.1 创建简单的 DAG 文件

在 `dags/` 目录下创建 `my_first_dag.py`:

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

# 定义默认参数
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
}

# 定义 DAG
dag = DAG(
    'my_first_dag',
    default_args=default_args,
    description='我的第一个 Airflow DAG',
    schedule_interval=None,  # 手动触发
    catchup=False,
    tags=['example'],
)

# 定义任务函数
def print_hello():
    print("Hello, Airflow!")
    return "任务执行成功"

# 创建任务
hello_task = PythonOperator(
    task_id='print_hello',
    python_callable=print_hello,
    dag=dag,
)

# 设置任务依赖（这里只有一个任务，所以不需要）
hello_task
```

### 4.2 创建更复杂的 DAG（示例）

如果需要处理数据的 DAG，创建 `process_data.py`:

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import json
import os

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
}

dag = DAG(
    'process_data',
    default_args=default_args,
    description='处理数据的 DAG',
    schedule_interval=None,
    catchup=False,
    tags=['data', 'processing'],
)

def read_data():
    """读取数据"""
    input_file = '/opt/airflow/data/input.json'
    print(f"读取文件: {input_file}")
    
    if not os.path.exists(input_file):
        print(f"警告: 文件 {input_file} 不存在")
        return None
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"成功读取 {len(data)} 条记录")
    return data

def process_data(**context):
    """处理数据"""
    # 从上一个任务获取数据
    data = context['ti'].xcom_pull(task_ids='read_data')
    
    if data is None:
        print("没有数据需要处理")
        return
    
    # 处理逻辑
    processed = []
    for item in data:
        # 示例：添加处理时间戳
        processed.append({
            **item,
            'processed_at': datetime.now().isoformat()
        })
    
    print(f"处理了 {len(processed)} 条记录")
    return processed

def save_data(**context):
    """保存数据"""
    processed_data = context['ti'].xcom_pull(task_ids='process_data')
    
    if processed_data is None:
        print("没有数据需要保存")
        return
    
    output_file = '/opt/airflow/data/output.json'
    print(f"保存到: {output_file}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(processed_data, f, ensure_ascii=False, indent=2)
    
    print(f"成功保存 {len(processed_data)} 条记录")

# 创建任务
read_task = PythonOperator(
    task_id='read_data',
    python_callable=read_data,
    dag=dag,
)

process_task = PythonOperator(
    task_id='process_data',
    python_callable=process_data,
    dag=dag,
)

save_task = PythonOperator(
    task_id='save_data',
    python_callable=save_data,
    dag=dag,
)

# 设置任务依赖
read_task >> process_task >> save_task
```

## 步骤 5: 启动 Airflow 服务

### 5.1 启动所有服务

```powershell
# 在项目根目录执行
cd C:\Users\JoeyC\my_airflow_project

# 启动所有服务（后台运行）
docker compose up -d
```

**这会启动**:
- PostgreSQL 数据库
- Airflow Web Server（Web UI）
- Airflow Scheduler（调度器）

### 5.2 检查服务状态

```powershell
# 查看所有服务状态
docker compose ps
```

**预期输出**:
```
NAME                    IMAGE                  STATUS
my_airflow_project-postgres-1       postgres:13            Up X minutes
my_airflow_project-airflow-webserver-1  apache/airflow:2.8.0   Up X minutes
my_airflow_project-airflow-scheduler-1  apache/airflow:2.8.0   Up X minutes
```

所有服务状态应该是 `Up`。

### 5.3 查看日志（如果需要）

```powershell
# 查看所有服务日志
docker compose logs

# 查看特定服务日志
docker compose logs airflow-scheduler
docker compose logs airflow-webserver

# 实时跟踪日志
docker compose logs -f airflow-scheduler
```

## 步骤 6: 访问 Web UI 并验证

### 6.1 打开 Web UI

1. 打开浏览器
2. 访问: http://localhost:8080
3. 登录信息:
   - 用户名: `airflow`
   - 密码: `airflow`

### 6.2 验证 DAG 加载

1. 在 Web UI 中，你应该能看到你创建的 DAG（如 `my_first_dag`）
2. 如果看不到，等待几秒钟（Scheduler 需要时间扫描 DAG 文件）
3. 检查 DAG 是否有错误（红色标记）

### 6.3 测试运行 DAG

1. 找到你的 DAG（如 `my_first_dag`）
2. 点击左侧的开关**启用 DAG**（如果显示为暂停状态）
3. 点击右侧的**播放按钮**手动触发运行
4. 点击 DAG 名称进入详情页
5. 在 **Graph View** 中查看任务执行状态
6. 点击任务查看日志

## 步骤 7: 准备数据文件（如果需要）

如果你的 DAG 需要处理数据文件：

### 7.1 创建输入文件

```powershell
# 在 data 目录创建示例输入文件
@"
[
    {"id": 1, "name": "项目A", "value": 100},
    {"id": 2, "name": "项目B", "value": 200},
    {"id": 3, "name": "项目C", "value": 300}
]
"@ | Out-File -FilePath "C:\Users\JoeyC\my_airflow_project\data\input.json" -Encoding UTF8
```

### 7.2 验证文件创建

```powershell
# 检查文件是否存在
Test-Path C:\Users\JoeyC\my_airflow_project\data\input.json

# 查看文件内容
Get-Content C:\Users\JoeyC\my_airflow_project\data\input.json
```

## 完整项目结构示例

```
my_airflow_project/
├── dags/
│   ├── __init__.py          # Python 包初始化文件（可选）
│   ├── my_first_dag.py      # 第一个 DAG
│   └── process_data.py      # 数据处理 DAG
├── logs/                    # 日志目录（自动生成）
│   └── ...
├── plugins/                 # 插件目录（可选）
├── data/                    # 数据目录
│   ├── input.json          # 输入文件
│   └── output.json         # 输出文件（运行后生成）
├── docker-compose.yml       # Docker Compose 配置
└── README.md               # 项目说明（可选）
```

## 常用命令参考

### 启动和停止

```powershell
# 启动服务
docker compose up -d

# 停止服务
docker compose down

# 停止并删除数据卷（包括数据库）
docker compose down -v

# 重启服务
docker compose restart
```

### 查看状态和日志

```powershell
# 查看服务状态
docker compose ps

# 查看日志
docker compose logs
docker compose logs -f airflow-scheduler  # 实时跟踪

# 查看特定服务的日志
docker compose logs airflow-webserver
```

### DAG 管理

```powershell
# 列出所有 DAG
docker compose exec airflow-webserver airflow dags list

# 测试 DAG（不实际执行）
docker compose exec airflow-webserver airflow dags test my_first_dag 2024-01-01

# 触发 DAG
docker compose exec airflow-webserver airflow dags trigger my_first_dag
```

### 数据库管理

```powershell
# 进入 PostgreSQL
docker compose exec postgres psql -U airflow -d airflow

# 备份数据库
docker compose exec postgres pg_dump -U airflow airflow > backup.sql

# 恢复数据库
docker compose exec -T postgres psql -U airflow airflow < backup.sql
```

## 故障排除

### 问题 1: 端口 8080 被占用

**解决方案**:
1. 修改 `docker-compose.yml` 中的端口映射
2. 或停止占用端口的其他服务

```powershell
# 查找占用 8080 端口的进程
netstat -ano | findstr :8080
```

### 问题 2: DAG 没有出现在 Web UI

**可能原因**:
- DAG 文件有语法错误
- Scheduler 还未扫描到文件
- DAG 定义有问题

**解决方案**:
```powershell
# 检查 DAG 语法
docker compose exec airflow-webserver python /opt/airflow/dags/my_first_dag.py

# 查看 Scheduler 日志
docker compose logs airflow-scheduler

# 手动触发 DAG 扫描
docker compose restart airflow-scheduler
```

### 问题 3: 任务执行失败

**检查步骤**:
1. 在 Web UI 中查看任务日志
2. 检查文件路径是否正确（使用容器内路径）
3. 检查文件权限
4. 查看错误信息

### 问题 4: 无法访问 Web UI

**检查步骤**:
```powershell
# 检查服务是否运行
docker compose ps

# 检查端口是否监听
netstat -ano | findstr :8080

# 查看 Web Server 日志
docker compose logs airflow-webserver
```

## 最佳实践

### 1. 项目组织

- 每个项目使用独立的目录
- 使用有意义的 DAG 名称
- 添加 DAG 描述和标签

### 2. 版本控制

```powershell
# 初始化 Git 仓库
cd C:\Users\JoeyC\my_airflow_project
git init

# 创建 .gitignore
@"
logs/
__pycache__/
*.pyc
.env
data/*.json
!data/.gitkeep
"@ | Out-File -FilePath ".gitignore" -Encoding UTF8

# 提交代码
git add .
git commit -m "Initial commit: Airflow project setup"
```

### 3. 环境变量

创建 `.env` 文件管理配置：

```env
AIRFLOW_UID=50000
AIRFLOW_WWW_USER_USERNAME=admin
AIRFLOW_WWW_USER_PASSWORD=your-password
POSTGRES_PASSWORD=your-db-password
```

然后在 `docker-compose.yml` 中引用。

### 4. 数据管理

- 将输入数据放在 `data/` 目录
- 输出文件也保存在 `data/` 目录
- 使用 `.gitignore` 排除敏感数据

### 5. 日志管理

- 定期清理旧日志
- 使用 Web UI 查看日志（更方便）
- 重要日志可以导出保存

## 下一步

1. **学习更多 Airflow 概念**
   - 任务依赖关系
   - 调度间隔设置
   - 错误处理和重试
   - XCom（任务间数据传递）

2. **扩展功能**
   - 添加更多任务
   - 使用不同的 Operator
   - 连接外部系统（数据库、API 等）

3. **优化配置**
   - 调整资源限制
   - 配置邮件通知
   - 设置任务超时

4. **部署到生产环境**
   - 修改默认密码
   - 配置 SSL/TLS
   - 设置备份策略

## 总结

创建新 Airflow 项目的步骤：

1. ✅ 创建项目目录结构
2. ✅ 创建 `docker-compose.yml` 文件
3. ✅ 初始化 Airflow
4. ✅ 创建 DAG 文件
5. ✅ 启动服务
6. ✅ 访问 Web UI 验证
7. ✅ 准备数据文件（如需要）
8. ✅ 测试运行 DAG

现在你已经可以在新文件夹中创建和管理 Airflow 工作流了！

