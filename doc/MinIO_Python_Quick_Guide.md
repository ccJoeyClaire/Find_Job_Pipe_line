# MinIO Python SDK 快速指南

## 安装

```bash
pip install minio
```

## 创建 MinIO 客户端实例

```python
from minio import Minio
from minio.error import S3Error

# 创建客户端
client = Minio(
    endpoint="localhost:9000",      # MinIO 服务地址
    access_key="minioadmin",         # 访问密钥
    secret_key="minioadmin",         # 秘密密钥
    secure=False                     # 是否使用 HTTPS
)
```

## 基本操作

### 1. 确保存储桶存在

```python
bucket_name = "my-bucket"

# 检查存储桶是否存在
if not client.bucket_exists(bucket_name):
    # 创建存储桶
    client.make_bucket(bucket_name)
```

### 2. 写入对象（上传文件）

```python
from io import BytesIO

# 方法 1: 上传字节数据
data = b"Hello, MinIO!"
data_stream = BytesIO(data)
client.put_object(
    bucket_name="my-bucket",
    object_name="path/to/file.txt",
    data=data_stream,
    length=len(data),
    content_type="text/plain"
)

# 方法 2: 上传本地文件
client.fput_object(
    bucket_name="my-bucket",
    object_name="path/to/file.txt",
    file_path="/local/path/to/file.txt"
)
```

### 3. 读取对象（下载文件）

```python
# 方法 1: 读取为字节数据
response = client.get_object("my-bucket", "path/to/file.txt")
data = response.read()
response.close()
response.release_conn()

# 方法 2: 下载到本地文件
client.fget_object(
    bucket_name="my-bucket",
    object_name="path/to/file.txt",
    file_path="/local/path/to/save.txt"
)
```

### 4. 列出对象（list_objects）

`list_objects()` 返回一个 **generator**，不能直接使用索引访问。

```python
bucket_name = "my-bucket"
html_dir = "raw/Linkedin_html/dt=2025-12-19"

# 列出对象（返回 generator）
objects = client.list_objects(
    bucket_name=bucket_name,
    prefix=html_dir,        # 可选：对象名称前缀过滤
    recursive=True          # 可选：是否递归列出子目录
)
```

#### 遍历所有对象

```python
# 遍历所有对象
for obj in objects:
    print(f"对象名称: {obj.object_name}, 大小: {obj.size} bytes")
    print(f"最后修改时间: {obj.last_modified}")
    print(f"ETag: {obj.etag}")
    print("-" * 50)
```

#### 获取单个对象用于测试

```python
# 方法 1: 使用 next() 获取第一个对象
objects = client.list_objects(bucket_name, prefix=html_dir, recursive=True)
first_obj = next(objects)
print(f"测试对象: {first_obj.object_name}, 大小: {first_obj.size} bytes")

# 读取第一个对象的内容
response = client.get_object(bucket_name, first_obj.object_name)
content = response.read()
response.close()
response.release_conn()
```

```python
# 方法 2: 使用 itertools.islice 获取前 N 个对象
from itertools import islice

objects = client.list_objects(bucket_name, prefix=html_dir, recursive=True)
# 获取前 5 个对象
first_5_objects = list(islice(objects, 5))
for obj in first_5_objects:
    print(f"对象: {obj.object_name}")
```

#### 对象属性说明

每个对象（`obj`）包含以下常用属性：

- `obj.object_name`: 对象的完整路径名称
- `obj.size`: 对象大小（字节）
- `obj.last_modified`: 最后修改时间（datetime 对象）
- `obj.etag`: 对象的 ETag（用于校验）
- `obj.content_type`: 内容类型（如果设置了）
- `obj.metadata`: 对象的元数据字典

#### 常用参数说明

- `bucket_name`: 存储桶名称（必需）
- `prefix`: 对象名称前缀，用于过滤（可选）
  - 例如：`prefix="raw/Linkedin_html/"` 只列出该路径下的对象
- `recursive`: 是否递归列出子目录（默认: False）
  - `True`: 递归列出所有子目录中的对象
  - `False`: 只列出当前层级（类似 `ls` 而非 `ls -R`）
- `start_after`: 从指定对象名称之后开始列出（可选，用于分页）

#### 完整示例：批量处理对象

```python
bucket_name = "jobdatabucket"
html_dir = "raw/Linkedin_html/dt=2025-12-19"

objects = client.list_objects(bucket_name, prefix=html_dir, recursive=True)

for obj in objects:
    print(f"处理对象: {obj.object_name}")
    
    # 读取对象内容
    response = client.get_object(bucket_name, obj.object_name)
    content = response.read()
    response.close()
    response.release_conn()
    
    # 处理内容（例如：解析 HTML）
    # process_content(content)
    
    # 注意：generator 只能遍历一次，如果需要多次使用，请转换为列表
    # objects_list = list(objects)  # 但要注意内存占用
```

## 完整示例

```python
from minio import Minio
from minio.error import S3Error
from io import BytesIO

# 1. 创建客户端
client = Minio(
    endpoint="localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)

bucket_name = "my-bucket"
object_name = "test/file.txt"

try:
    # 2. 确保存储桶存在
    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)
    
    # 3. 写入数据
    data = b"Hello, MinIO!"
    client.put_object(
        bucket_name=bucket_name,
        object_name=object_name,
        data=BytesIO(data),
        length=len(data)
    )
    print("✅ 写入成功")
    
    # 4. 读取数据
    response = client.get_object(bucket_name, object_name)
    content = response.read().decode('utf-8')
    response.close()
    response.release_conn()
    print(f"📖 读取内容: {content}")
    
except S3Error as e:
    print(f"❌ 错误: {e}")
```

## 常用参数说明

### MinIO 客户端参数

- `endpoint`: MinIO 服务地址，格式 `host:port`
- `access_key`: 访问密钥（默认: minioadmin）
- `secret_key`: 秘密密钥（默认: minioadmin）
- `secure`: 是否使用 HTTPS（默认: False）

### 对象操作参数

- `bucket_name`: 存储桶名称
- `object_name`: 对象路径（支持路径，如 `folder/subfolder/file.txt`）
- `content_type`: MIME 类型（如 `text/plain`, `application/json`, `image/png`）

### list_objects 参数

- `prefix`: 对象名称前缀，用于过滤（可选）
- `recursive`: 是否递归列出子目录（默认: False）
- `start_after`: 从指定对象名称之后开始列出（可选，用于分页）

**注意**: `list_objects()` 返回的是 **generator**，不能直接使用索引（如 `objects[0]`），需要使用 `next()` 或 `for` 循环来访问。

---

# Parquet 核心操作指南

## 安装

```bash
pip install pyarrow pandas
```

## 使用 PyArrow 操作 Parquet（内存操作）

### 1. DataFrame 转 Parquet bytes

```python
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from io import BytesIO

# 准备 DataFrame
df = pd.DataFrame({
    'id': [1, 2, 3],
    'name': ['Alice', 'Bob', 'Charlie']
})

# 转换为 Parquet bytes
buffer = BytesIO()
table = pa.Table.from_pandas(df)
pq.write_table(table, buffer, compression='snappy')
parquet_bytes = buffer.getvalue()
```

### 2. Parquet bytes 转 DataFrame

```python
# 从 Parquet bytes 读取
buffer = BytesIO(parquet_bytes)
table = pq.read_table(buffer)
df = table.to_pandas()
```

## 使用 Pandas 操作 Parquet（本地文件）

### 1. 保存 DataFrame 为 Parquet 文件

```python
import pandas as pd

df = pd.DataFrame({
    'id': [1, 2, 3],
    'name': ['Alice', 'Bob', 'Charlie']
})

# 保存到本地文件
df.to_parquet('data.parquet', compression='snappy', index=False)
```

### 2. 读取 Parquet 文件为 DataFrame

```python
# 从本地文件读取
df = pd.read_parquet('data.parquet')
```

## 完整示例：结合 MinIO 使用

```python
from minio import Minio
from io import BytesIO
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

# 1. 创建 MinIO 客户端
client = Minio(
    endpoint="localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)

bucket_name = "my-bucket"

# 2. 准备数据
df = pd.DataFrame({
    'job_id': [1, 2, 3],
    'title': ['Engineer', 'Manager', 'Analyst']
})

# 3. 转换为 Parquet bytes
buffer = BytesIO()
table = pa.Table.from_pandas(df)
pq.write_table(table, buffer, compression='snappy')
parquet_bytes = buffer.getvalue()

# 4. 上传到 MinIO
buffer.seek(0)
client.put_object(
    bucket_name=bucket_name,
    object_name="data/jobs.parquet",
    data=buffer,
    length=len(parquet_bytes),
    content_type='application/octet-stream'
)

# 5. 从 MinIO 下载并读取
response = client.get_object(bucket_name, "data/jobs.parquet")
parquet_data = response.read()
response.close()
response.release_conn()

# 6. 转换为 DataFrame
buffer = BytesIO(parquet_data)
table = pq.read_table(buffer)
df_loaded = table.to_pandas()
print(df_loaded)
```

## 常用参数说明

- `compression`: 压缩算法（`snappy`, `gzip`, `brotli`, `zstd`, `lz4`）
- `index`: 是否保存索引（pandas `to_parquet` 参数）
- `preserve_index`: 是否保留索引（pyarrow `from_pandas` 参数）

---

# DuckDB 核心操作指南

## 安装

```bash
pip install duckdb
```

## 基本连接

```python
import duckdb

# 创建内存数据库连接
conn = duckdb.connect()

# 或者连接到持久化数据库文件
conn = duckdb.connect('database.duckdb')

# 执行查询并返回 DataFrame
result = conn.execute("SELECT 1 as value").fetchdf()
print(result)
```

## Parquet 查询

### 1. 查询单个 Parquet 文件

```python
import duckdb

conn = duckdb.connect()

# 方法 1: 直接查询文件路径
df = conn.execute("""
    SELECT *
    FROM 'data/jobs.parquet'
    WHERE title LIKE '%Engineer%'
    LIMIT 10
""").fetchdf()

# 方法 2: 使用 read_parquet 函数
df = conn.execute("""
    SELECT job_id, title, company
    FROM read_parquet('data/jobs.parquet')
    WHERE salary > 100000
""").fetchdf()
```

### 2. 查询多个 Parquet 文件（通配符）

```python
import duckdb

conn = duckdb.connect()

# 使用通配符查询多个文件
df = conn.execute("""
    SELECT *
    FROM read_parquet('data/jobs_*.parquet')
    WHERE title LIKE '%Data%'
    ORDER BY job_id
""").fetchdf()

# 查询目录下所有 Parquet 文件
df = conn.execute("""
    SELECT *
    FROM read_parquet('data/staging/job_table/dt=2024-12-*/jobs.parquet')
    WHERE processed_date >= '2024-12-01'
""").fetchdf()
```

### 3. 查询多个 Parquet 文件（列表）

```python
import duckdb

conn = duckdb.connect()

# 使用列表指定多个文件
df = conn.execute("""
    SELECT *
    FROM read_parquet([
        'data/jobs_2024-12-01.parquet',
        'data/jobs_2024-12-02.parquet',
        'data/jobs_2024-12-03.parquet'
    ])
    WHERE company = 'Tech Corp'
""").fetchdf()
```

### 4. 查询分区数据（多目录）

```python
import duckdb

conn = duckdb.connect()

# 查询多个日期分区的数据
df = conn.execute("""
    SELECT 
        dt,
        COUNT(*) as job_count,
        AVG(salary) as avg_salary
    FROM read_parquet([
        'staging/job_table/dt=2024-12-01/jobs.parquet',
        'staging/job_table/dt=2024-12-02/jobs.parquet',
        'staging/job_table/dt=2024-12-03/jobs.parquet'
    ])
    GROUP BY dt
    ORDER BY dt
""").fetchdf()
```

### 5. 使用 glob 模式查询

```python
import duckdb

conn = duckdb.connect()

# 使用 glob 模式匹配多个文件
df = conn.execute("""
    SELECT *
    FROM read_parquet('data/**/*.parquet')
    WHERE title LIKE '%Engineer%'
""").fetchdf()
```

## JSON 查询

### 1. 查询单个 JSON 文件

```python
import duckdb

conn = duckdb.connect()

# 方法 1: 直接查询 JSON 文件
df = conn.execute("""
    SELECT *
    FROM read_json('data/jobs.json')
    WHERE title LIKE '%Engineer%'
""").fetchdf()

# 方法 2: 查询 JSON 数组
df = conn.execute("""
    SELECT 
        job_id,
        title,
        company,
        salary
    FROM read_json('data/jobs.json', format='array')
    WHERE salary > 100000
""").fetchdf()
```

### 2. 查询多个 JSON 文件

```python
import duckdb

conn = duckdb.connect()

# 使用通配符查询多个 JSON 文件
df = conn.execute("""
    SELECT *
    FROM read_json('data/jobs_*.json')
    WHERE company = 'Tech Corp'
    ORDER BY job_id
""").fetchdf()

# 查询目录下所有 JSON 文件
df = conn.execute("""
    SELECT *
    FROM read_json('raw/Linkedin_html/dt=2024-12-*/*.json')
    WHERE processed_date >= '2024-12-01'
""").fetchdf()
```

### 3. 查询 JSON Lines (NDJSON) 文件

```python
import duckdb

conn = duckdb.connect()

# 查询 JSON Lines 格式文件（每行一个 JSON 对象）
df = conn.execute("""
    SELECT *
    FROM read_json('data/jobs.jsonl', format='newline_delimited')
    WHERE title LIKE '%Data%'
""").fetchdf()

# 查询多个 JSON Lines 文件
df = conn.execute("""
    SELECT *
    FROM read_json([
        'data/jobs_2024-12-01.jsonl',
        'data/jobs_2024-12-02.jsonl'
    ], format='newline_delimited')
    WHERE salary > 100000
""").fetchdf()
```

### 4. 查询嵌套 JSON 结构

```python
import duckdb

conn = duckdb.connect()

# 查询嵌套 JSON 字段
df = conn.execute("""
    SELECT 
        job_id,
        title,
        company.name as company_name,
        company.location as company_location,
        skills[1] as primary_skill
    FROM read_json('data/jobs.json')
    WHERE company.size > 1000
""").fetchdf()
```

## 多文件查询高级用法

### 1. 联合查询多个数据源

```python
import duckdb

conn = duckdb.connect()

# 联合查询 Parquet 和 JSON 文件
df = conn.execute("""
    SELECT 
        job_id,
        title,
        company,
        'parquet' as source
    FROM read_parquet('data/jobs_parquet/*.parquet')
    
    UNION ALL
    
    SELECT 
        job_id,
        title,
        company,
        'json' as source
    FROM read_json('data/jobs_json/*.json')
    
    ORDER BY job_id
""").fetchdf()
```

### 2. 跨文件 JOIN 操作

```python
import duckdb

conn = duckdb.connect()

# JOIN 不同文件中的数据
df = conn.execute("""
    SELECT 
        j.job_id,
        j.title,
        j.company_id,
        c.company_name,
        c.industry
    FROM read_parquet('staging/job_table/dt=2024-12-01/jobs.parquet') j
    JOIN read_parquet('staging/company_table/dt=2024-12-01/companies.parquet') c
        ON j.company_id = c.company_id
    WHERE j.salary > 100000
""").fetchdf()
```

### 3. 聚合多个文件的数据

```python
import duckdb

conn = duckdb.connect()

# 聚合多个日期分区的数据
df = conn.execute("""
    SELECT 
        company,
        COUNT(*) as total_jobs,
        AVG(salary) as avg_salary,
        MIN(salary) as min_salary,
        MAX(salary) as max_salary
    FROM read_parquet('staging/job_table/dt=2024-12-*/jobs.parquet')
    GROUP BY company
    HAVING COUNT(*) > 10
    ORDER BY total_jobs DESC
""").fetchdf()
```

### 4. 使用 CTE 组织复杂查询

```python
import duckdb

conn = duckdb.connect()

# 使用 CTE 组织多文件查询
df = conn.execute("""
    WITH recent_jobs AS (
        SELECT *
        FROM read_parquet('staging/job_table/dt=2024-12-*/jobs.parquet')
        WHERE processed_date >= '2024-12-01'
    ),
    company_info AS (
        SELECT *
        FROM read_parquet('staging/company_table/dt=2024-12-*/companies.parquet')
    )
    SELECT 
        r.job_id,
        r.title,
        r.salary,
        c.company_name,
        c.industry
    FROM recent_jobs r
    JOIN company_info c ON r.company_id = c.company_id
    WHERE r.salary > 100000
    ORDER BY r.salary DESC
""").fetchdf()
```

## 与 MinIO 结合使用

### 1. 配置 DuckDB 连接 MinIO (S3)

```python
import duckdb

conn = duckdb.connect()

# 安装并加载 httpfs 扩展（支持 S3/MinIO）
conn.execute("INSTALL httpfs")
conn.execute("LOAD httpfs")

# 配置 MinIO 连接
conn.execute("""
    SET s3_endpoint='localhost:9000';
    SET s3_access_key_id='minioadmin';
    SET s3_secret_access_key='minioadmin';
    SET s3_use_ssl=false;
    SET s3_url_style='path';
""")
```

### 2. 查询 MinIO 中的 Parquet 文件

```python
import duckdb

conn = duckdb.connect()
conn.execute("INSTALL httpfs")
conn.execute("LOAD httpfs")
conn.execute("SET s3_endpoint='localhost:9000'")
conn.execute("SET s3_access_key_id='minioadmin'")
conn.execute("SET s3_secret_access_key='minioadmin'")
conn.execute("SET s3_use_ssl=false")
conn.execute("SET s3_url_style='path'")

# 查询 MinIO 中的 Parquet 文件
df = conn.execute("""
    SELECT *
    FROM read_parquet('s3://jobdatabucket/staging/job_table/dt=2024-12-01/jobs.parquet')
    WHERE title LIKE '%Engineer%'
""").fetchdf()
```

### 3. 查询 MinIO 中的多个文件

```python
import duckdb

conn = duckdb.connect()
# ... 配置 MinIO 连接（同上）

# 查询 MinIO 中多个日期分区的数据
df = conn.execute("""
    SELECT 
        dt,
        COUNT(*) as job_count
    FROM read_parquet([
        's3://jobdatabucket/staging/job_table/dt=2024-12-01/jobs.parquet',
        's3://jobdatabucket/staging/job_table/dt=2024-12-02/jobs.parquet',
        's3://jobdatabucket/staging/job_table/dt=2024-12-03/jobs.parquet'
    ])
    GROUP BY dt
""").fetchdf()
```

### 4. 查询 MinIO 中的 JSON 文件

```python
import duckdb

conn = duckdb.connect()
# ... 配置 MinIO 连接（同上）

# 查询 MinIO 中的 JSON 文件
df = conn.execute("""
    SELECT *
    FROM read_json('s3://jobdatabucket/raw/Linkedin_html/dt=2024-12-01/*.json')
    WHERE title LIKE '%Data%'
""").fetchdf()
```

## 完整示例

```python
import duckdb
from minio import Minio
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from io import BytesIO

# 1. 创建 MinIO 客户端
minio_client = Minio(
    endpoint="localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)

bucket_name = "jobdatabucket"

# 2. 准备数据并上传到 MinIO
df = pd.DataFrame({
    'job_id': [1, 2, 3],
    'title': ['Data Engineer', 'Data Scientist', 'ML Engineer'],
    'salary': [120000, 150000, 140000]
})

buffer = BytesIO()
table = pa.Table.from_pandas(df)
pq.write_table(table, buffer, compression='snappy')
parquet_bytes = buffer.getvalue()

buffer.seek(0)
minio_client.put_object(
    bucket_name=bucket_name,
    object_name="staging/job_table/dt=2024-12-01/jobs.parquet",
    data=buffer,
    length=len(parquet_bytes),
    content_type='application/octet-stream'
)

# 3. 使用 DuckDB 查询 MinIO 中的数据
conn = duckdb.connect()
conn.execute("INSTALL httpfs")
conn.execute("LOAD httpfs")
conn.execute("SET s3_endpoint='localhost:9000'")
conn.execute("SET s3_access_key_id='minioadmin'")
conn.execute("SET s3_secret_access_key='minioadmin'")
conn.execute("SET s3_use_ssl=false")
conn.execute("SET s3_url_style='path'")

# 查询数据
result_df = conn.execute("""
    SELECT 
        job_id,
        title,
        salary
    FROM read_parquet('s3://jobdatabucket/staging/job_table/dt=2024-12-01/jobs.parquet')
    WHERE salary > 130000
    ORDER BY salary DESC
""").fetchdf()

print(result_df)
```

## 常用参数说明

### read_parquet 参数

- `filename`: 文件路径（支持通配符 `*` 和 `**`）
- `columns`: 指定要读取的列（列表）
- `compression`: 压缩格式（自动检测）

### read_json 参数

- `filename`: 文件路径（支持通配符）
- `format`: JSON 格式
  - `'auto'`: 自动检测（默认）
  - `'array'`: JSON 数组格式
  - `'newline_delimited'`: JSON Lines 格式
  - `'records'`: 每行一个 JSON 对象
- `compression`: 压缩格式（`'auto'`, `'gzip'`, `'zstd'` 等）

### MinIO/S3 配置参数

- `s3_endpoint`: MinIO 服务地址（格式: `host:port`）
- `s3_access_key_id`: 访问密钥
- `s3_secret_access_key`: 秘密密钥
- `s3_use_ssl`: 是否使用 HTTPS（MinIO 通常为 `false`）
- `s3_url_style`: URL 风格（MinIO 使用 `'path'`）

## 性能优化建议

1. **列选择**: 只查询需要的列，减少 I/O
   ```python
   df = conn.execute("""
       SELECT job_id, title  -- 只选择需要的列
       FROM read_parquet('data/jobs.parquet')
   """).fetchdf()
   ```

2. **谓词下推**: 在查询中使用 WHERE 子句，DuckDB 会自动优化
   ```python
   df = conn.execute("""
       SELECT *
       FROM read_parquet('data/jobs.parquet')
       WHERE salary > 100000  -- 谓词下推，只读取相关数据
   """).fetchdf()
   ```

3. **分区剪枝**: 使用分区字段过滤，减少文件扫描
   ```python
   df = conn.execute("""
       SELECT *
       FROM read_parquet('staging/job_table/dt=2024-12-01/jobs.parquet')
       WHERE dt = '2024-12-01'  -- 分区字段过滤
   """).fetchdf()
   ```

4. **批量查询**: 对于多个文件，使用列表或通配符一次性查询
   ```python
   # ✅ 推荐：一次性查询多个文件
   df = conn.execute("""
       SELECT * FROM read_parquet('data/jobs_*.parquet')
   """).fetchdf()
   
   # ❌ 不推荐：循环查询单个文件
   # for file in files:
   #     df = conn.execute(f"SELECT * FROM read_parquet('{file}')").fetchdf()
   ```
