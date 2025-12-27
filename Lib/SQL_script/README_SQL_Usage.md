# SQL 文件使用说明

## MinIO 配置持久性

### DuckDB 行为说明

DuckDB 的 `SET` 配置命令在**同一个连接/会话**中是持久的。这意味着：

- ✅ **如果 dbcode 插件使用同一个 DuckDB 连接**：执行一次 `init_minio.sql` 后，配置会保留，其他 SQL 文件**不需要**重复设置
- ❌ **如果 dbcode 插件为每个 SQL 文件创建新连接**：每个文件都需要重新设置配置

### 如何测试

1. **测试方法**：
   ```sql
   -- 1. 先执行 init_minio.sql
   -- 2. 然后执行以下测试查询（不包含配置）
   SELECT current_setting('s3_endpoint') as endpoint;
   ```
   
   如果返回 `localhost:9000`，说明配置已持久化，其他文件不需要重复设置。

2. **如果测试失败**（返回空或错误）：
   - 说明 dbcode 为每个文件创建了新连接
   - 需要在每个 SQL 文件开头添加配置

### 推荐方案

#### 方案 A：如果配置已持久化（推荐）

如果测试确认配置已持久化，可以：

1. **执行一次** `init_minio.sql` 初始化配置
2. **其他 SQL 文件**可以移除配置部分，只保留查询语句

例如 `read_co_info2.sql` 可以简化为：
```sql
-- 假设已执行 init_minio.sql
select * 
from read_parquet('s3://jobdatabucket/stagging/company_info/dt=20251223/company_info_with_score.parquet')
```

#### 方案 B：如果配置不持久化（保险方案）

如果测试确认配置不持久化，或者不确定：

1. **保留每个文件中的配置**（当前方案）
2. 重复设置是安全的，不会造成问题

### 当前文件状态

- ✅ `init_minio.sql` - 完整的配置初始化文件
- ✅ `read_co_info.sql` - 包含配置（如果方案 B）
- ✅ `read_co_info2.sql` - 包含配置（如果方案 B）

### 使用 Exe_SQL 类

如果使用 Python 的 `Exe_SQL` 类执行 SQL：

- ✅ **不需要**在每个 SQL 文件中添加配置
- ✅ `Exe_SQL.connect()` 会自动设置配置
- ✅ 同一个 `Exe_SQL` 实例执行多个文件时，配置会持久化


