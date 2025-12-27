# Lakehouse vs Traditional Database Architecture

## Overview

This document explains the differences between the Lakehouse architecture (used in this project) and traditional relational database architecture with primary/foreign keys.

## Architecture Comparison

### Traditional Relational Database (主外键架构)

```
┌─────────────────────────────────────────┐
│      Application Layer                  │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│   Relational Database (PostgreSQL)      │
│                                         │
│   ┌─────────────┐    ┌─────────────┐   │
│   │  jobs       │    │  companies  │   │
│   │─────────────│    │─────────────│   │
│   │ id (PK)     │───▶│ id (PK)     │   │
│   │ company_id  │    │ name        │   │
│   │ title       │    │ description │   │
│   │ ...         │    │ ...         │   │
│   └─────────────┘    └─────────────┘   │
│                                         │
│   ┌─────────────┐                       │
│   │  skills     │                       │
│   │─────────────│                       │
│   │ id (PK)     │                       │
│   │ job_id (FK) │                       │
│   │ skill_name  │                       │
│   └─────────────┘                       │
└─────────────────────────────────────────┘
```

**Characteristics:**
- **Schema-on-Write**: Schema must be defined before writing data
- **Normalized Structure**: Data split into multiple related tables
- **ACID Transactions**: Strong consistency guarantees
- **Primary/Foreign Keys**: Enforced referential integrity
- **SQL Queries**: Optimized for transactional queries
- **Storage**: Row-oriented (optimized for updates)

### Lakehouse Architecture (湖仓架构)

```
┌─────────────────────────────────────────┐
│      Application Layer                  │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│   Object Storage (MinIO)                │
│                                         │
│   raw/                                  │
│   ├── linkedin_html/                    │
│   │   └── dt=2024-12-11/               │
│   │       ├── job_12345.html           │
│   │       └── job_67890.html           │
│                                         │
│   staging/                              │
│   ├── job_table/                        │
│   │   └── dt=2024-12-11/               │
│   │       └── jobs.parquet             │
│   ├── company_table/                    │
│   │   └── dt=2024-12-11/               │
│   │       └── companies.parquet        │
│                                         │
│   curated/                              │
│   ├── job_features/                     │
│   │   └── dt=2024-12-11/               │
│   │       └── job_features.parquet     │
│   └── job_company_joined/               │
│       └── dt=2024-12-11/               │
│           └── job_company.parquet      │
└─────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│   Query Engine (DuckDB)                 │
│   - Reads Parquet files                 │
│   - Schema-on-Read                      │
│   - Columnar queries                    │
└─────────────────────────────────────────┘
```

**Characteristics:**
- **Schema-on-Read**: Schema inferred when reading data
- **Denormalized Structure**: Data stored as files (Parquet)
- **Eventual Consistency**: Optimized for analytics, not transactions
- **No Enforced Keys**: Referential integrity handled in application layer
- **Columnar Storage**: Optimized for analytical queries
- **Time-based Partitioning**: Data organized by date (dt=YYYY-MM-DD)

## Key Differences

### 1. Data Organization (数据组织方式)

#### Traditional DB (主外键架构)
```sql
-- Normalized tables with relationships
CREATE TABLE jobs (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id),
    title VARCHAR(255),
    ...
);

CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    ...
);

-- Query requires JOINs
SELECT j.title, c.name
FROM jobs j
JOIN companies c ON j.company_id = c.id;
```

**特点：**
- 数据被**拆分**到多个表（规范化）
- 通过**主外键**维护关系
- 查询需要 **JOIN** 操作
- 数据**冗余少**，但查询可能复杂

#### Lakehouse (湖仓架构)
```python
# Denormalized Parquet files
# jobs.parquet contains all job data
# companies.parquet contains all company data
# job_company.parquet contains pre-joined data

# Query can be simple (if pre-joined)
SELECT title, company_name
FROM 'job_company.parquet'
```

**特点：**
- 数据以**文件**形式存储（Parquet）
- 可以存储**预连接**的数据（denormalized）
- 查询**不需要 JOIN**（如果数据已预连接）
- 数据可能有**冗余**，但查询更快

### 2. Schema Management (模式管理)

#### Traditional DB
- **Schema-on-Write**: 写入前必须定义表结构
- **严格类型**: 每个字段都有固定类型
- **约束检查**: 主键、外键、NOT NULL 等在写入时检查
- **修改困难**: ALTER TABLE 可能很慢，影响性能

```sql
-- Must define schema first
CREATE TABLE jobs (
    id INTEGER PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    company_id INTEGER REFERENCES companies(id)
);

-- Insert fails if schema doesn't match
INSERT INTO jobs VALUES (1, 'Engineer', 100);  -- Fails if company_id=100 doesn't exist
```

#### Lakehouse
- **Schema-on-Read**: 读取时推断模式
- **灵活类型**: Parquet 文件可以包含不同结构的数据
- **无约束检查**: 写入时不检查外键等约束
- **易于扩展**: 添加新字段只需写入新文件

```python
# Write data without strict schema
df = pd.DataFrame({
    'job_id': [1, 2],
    'title': ['Engineer', 'Manager'],
    'company_id': [100, 200]  # No foreign key check
})
df.to_parquet('jobs.parquet')

# Schema inferred when reading
df = pd.read_parquet('jobs.parquet')
```

### 3. Data Updates (数据更新)

#### Traditional DB
- **In-place Updates**: UPDATE 语句直接修改数据
- **实时一致性**: 更新立即生效
- **事务支持**: ACID 保证数据一致性

```sql
-- Update existing record
UPDATE jobs SET title = 'Senior Engineer' WHERE id = 1;
-- Change is immediate and consistent
```

#### Lakehouse
- **Append-only**: 通常追加新文件，不修改旧文件
- **时间分区**: 按日期组织，每天生成新文件
- **版本控制**: 通过文件版本管理历史数据

```python
# Append new data (new file for new date)
df_new = process_today_data()
save_dataframe_to_minio(
    df=df_new,
    zone="staging",
    table_name="job_table",
    date="2024-12-12",  # New date = new file
    filename="jobs.parquet"
)

# Old data (2024-12-11) remains unchanged
```

### 4. Query Performance (查询性能)

#### Traditional DB
- **Row-oriented**: 按行存储，适合点查询
- **索引优化**: B-tree 索引加速查找
- **适合**: 事务性查询（OLTP）

```sql
-- Fast: Uses index on id
SELECT * FROM jobs WHERE id = 12345;

-- Slower: Full table scan
SELECT COUNT(*) FROM jobs WHERE title LIKE '%Engineer%';
```

#### Lakehouse
- **Column-oriented**: Parquet 按列存储，适合分析查询
- **列式压缩**: 相同类型数据压缩率高
- **适合**: 分析性查询（OLAP）

```python
# Fast: Only reads 'title' column
df = duckdb.query("""
    SELECT COUNT(*) 
    FROM 'jobs.parquet' 
    WHERE title LIKE '%Engineer%'
""")
# DuckDB only reads the 'title' column, not entire rows
```

### 5. Scalability (可扩展性)

#### Traditional DB
- **垂直扩展**: 需要更强的服务器
- **连接限制**: 数据库连接数有限
- **单机限制**: 通常单机运行

#### Lakehouse
- **水平扩展**: 可以添加更多存储节点
- **无连接限制**: 文件系统无连接概念
- **分布式友好**: 数据可以分布在多个节点

### 6. Cost (成本)

#### Traditional DB
- **计算资源**: 需要强大的数据库服务器
- **存储成本**: 行式存储压缩率较低
- **维护成本**: 需要 DBA 管理

#### Lakehouse
- **存储成本**: 对象存储（MinIO/S3）成本低
- **计算分离**: 计算和存储分离，按需使用
- **维护简单**: 文件系统管理更简单

## When to Use Each Architecture

### Use Traditional DB (主外键架构) When:
- ✅ 需要**强一致性**（银行交易、订单系统）
- ✅ **频繁更新**（用户信息、库存管理）
- ✅ **事务处理**（OLTP 场景）
- ✅ **复杂关系查询**（需要多表 JOIN）
- ✅ **数据量较小**（< 100GB）

### Use Lakehouse (湖仓架构) When:
- ✅ **分析为主**（数据仓库、BI 报表）
- ✅ **批量处理**（ETL 管道、数据转换）
- ✅ **历史数据保留**（时间序列数据）
- ✅ **大规模数据**（TB 到 PB 级别）
- ✅ **灵活模式**（数据结构经常变化）
- ✅ **成本敏感**（需要低成本存储）

## Hybrid Approach (混合方案)

在实际项目中，可以**结合使用**两种架构：

```
┌─────────────────┐
│  OLTP System    │  ← Traditional DB (PostgreSQL)
│  (Transactions)  │     - User management
│                 │     - Order processing
└────────┬────────┘
         │
         │ ETL Pipeline
         ▼
┌─────────────────┐
│  Lakehouse      │  ← MinIO + Parquet
│  (Analytics)    │     - Data warehouse
│                 │     - BI reports
└─────────────────┘
```

**Example in Your Project:**
- **PostgreSQL**: Airflow metadata, user management (OLTP)
- **MinIO + Parquet**: Job data, analytics, historical data (OLAP)

## Summary Table

| Feature | Traditional DB | Lakehouse |
|---------|---------------|-----------|
| **Storage** | Row-oriented | Column-oriented (Parquet) |
| **Schema** | Schema-on-Write | Schema-on-Read |
| **Updates** | In-place | Append-only |
| **Consistency** | Strong (ACID) | Eventual |
| **Keys** | Enforced (PK/FK) | Application-level |
| **Queries** | JOINs required | Pre-joined possible |
| **Scale** | Vertical | Horizontal |
| **Cost** | Higher (compute) | Lower (storage) |
| **Use Case** | OLTP | OLAP |

## Conclusion

Your Lakehouse architecture is **optimized for analytics and data processing**, while traditional databases are **optimized for transactions and consistency**. The choice depends on your use case:

- **This project**: Analytics, batch processing, historical data → **Lakehouse is appropriate**
- **If you needed**: Real-time updates, transactions, strict consistency → **Traditional DB would be better**

The architecture you've chosen fits perfectly for a **data pipeline and analytics use case**!

