# 🎯 Intelligent Job Pipeline - 智能职位数据管道系统
@

[English](readme_EN.md) | [中文](readme.md)

> 基于湖仓架构（Lakehouse）的端到端数据工程实践项目，实现从 LinkedIn 职位数据采集、处理、分析到智能筛选的完整数据管道。

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Airflow](https://img.shields.io/badge/Airflow-2.8.0-orange.svg)](https://airflow.apache.org/)
[![MinIO](https://img.shields.io/badge/MinIO-S3--compatible-green.svg)](https://min.io/)
[![DuckDB](https://img.shields.io/badge/DuckDB-Analytics-yellow.svg)](https://duckdb.org/)
[![Spark](https://img.shields.io/badge/Spark-3.5.7-red.svg)](https://spark.apache.org/)

---

## 📋 目录

- [项目概览](#-项目概览)
- [系统架构](#-系统架构)
- [技术栈](#-技术栈)
- [数据架构](#-数据架构)
- [核心功能](#-核心功能)
- [快速开始](#-快速开始)
- [项目结构](#-项目结构)
- [数据管道](#-数据管道)
- [设计亮点](#-设计亮点)
- [文档](#-文档)

---

## 🎯 项目概览

本项目是一个**生产级的数据工程实践项目**，展示了从数据采集到智能分析的完整数据管道构建能力。项目采用 **Medallion 架构**（Bronze/Silver/Gold 三层数据分层），结合现代数据栈技术，实现了 LinkedIn 职位数据的自动化采集、处理、分析和智能筛选。

### 核心价值

- ✅ **端到端数据工程能力**：从 Web 爬取到数据存储、处理、分析的完整流程
- ✅ **湖仓架构实践**：采用 Medallion 架构，实现数据的分层治理和 Schema-on-Read
- ✅ **现代数据栈**：集成 Airflow、MinIO、DuckDB、Spark 等主流数据工具
- ✅ **智能化处理**：集成 LLM 进行公司评估和职位描述分解
- ✅ **生产级设计**：容器化部署、模块化代码、可扩展架构

---

## 🏗️ 系统架构

### 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                      Data Sources                            │
│                   (LinkedIn Job Postings)                    │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    Apache Airflow                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │Linkedin_Scrape│  │Data_Process_ │  │  Custom DAGs │      │
│  │     DAG      │  │   Pipeline   │  │              │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼─────────────────┼──────────────────┼─────────────┘
          │                 │                  │
          ▼                 ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│                    MinIO (S3-compatible)                     │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Bronze Layer (Raw JSON)                           │    │
│  │  bronze/raw_json/dt=YYYYMMDD/*.json               │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Silver Layer (Processed Data)                      │    │
│  │  silver/company_info/dt=*/company_info.parquet    │    │
│  │  silver/JD_Processed/dt=*/JD_Processed.parquet    │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Gold Layer (Analytical Ready)                      │    │
│  │  gold/target_company/dt=*/target_company.parquet  │    │
│  │  gold/target_JD/dt=*/target_JD.parquet            │    │
│  └────────────────────────────────────────────────────┘    │
└───────────────────────┬───────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              Query & Analytics Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   DuckDB     │  │    Spark     │  │   Python     │      │
│  │  (SQL Query) │  │ (Distributed)│  │  (Analysis)  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### 数据流转

```
LinkedIn HTML 
    ↓ [Selenium Scraper]
Raw HTML (MinIO: raw/Linkedin_html/)
    ↓ [HTML Parser + ThreadPoolExecutor]
Bronze JSON (MinIO: bronze/raw_json/)
    ↓ [LLM Analysis + Data Processing]
Silver Parquet (MinIO: silver/company_info/, silver/JD_Processed/)
    ↓ [DuckDB SQL Filtering]
Gold Parquet (MinIO: gold/target_company/, gold/target_JD/)
    ↓ [Analytics & Insights]
Final Results
```

---

## 🛠️ 技术栈

### 数据编排
- **Apache Airflow 2.8.0** - 工作流编排和任务调度

### 数据存储
- **MinIO** - S3 兼容的对象存储，作为数据湖存储层
- **Parquet** - 列式存储格式，优化查询性能

### 计算引擎
- **DuckDB** - 高性能分析型数据库，用于 SQL 查询和数据分析
- **Apache Spark 3.5.7** - 分布式计算引擎（可选，用于大规模数据处理）

### 数据采集
- **Selenium** - Web 自动化，用于 LinkedIn 职位数据爬取
- **BeautifulSoup** - HTML 解析

### 数据处理
- **Python 3.8+** - 主要编程语言
- **Pandas** - 数据处理和分析
- **PyArrow** - Parquet 文件读写

### AI/LLM 集成
- **DeepSeek API** - LLM 服务，用于公司评估和职位描述分解

### 容器化
- **Docker & Docker Compose** - 容器化部署

---

## 📊 数据架构

### Medallion 架构（三层数据分层）

本项目采用 **Medallion 架构**，这是现代数据湖仓架构的最佳实践：

#### 1. **Bronze Layer（原始数据层）**
- **目的**：存储原始、未处理的数据，作为数据源的真实记录
- **格式**：JSON 文件
- **数据来源**：HTML 解析后的结构化 JSON
- **存储路径**：`bronze/raw_json/dt=YYYYMMDD/*.json`
- **特点**：
  - 保留原始数据，支持数据回溯
  - 按日期分区，便于数据管理
  - 不可变数据（Immutable）

#### 2. **Silver Layer（清洗数据层）**
- **目的**：存储清洗、标准化和增强后的数据
- **格式**：Parquet 文件
- **处理内容**：
  - 公司信息评估（使用 LLM 进行多维度评分）
  - 职位描述分解（提取关键词、学历要求、工作经验等）
- **存储路径**：
  - `silver/company_info/dt=*/company_info_with_score.parquet`
  - `silver/JD_Processed/dt=*/JD_Processed.parquet`
- **特点**：
  - 结构化数据，便于查询
  - 列式存储，查询性能优化
  - 支持数据质量检查

#### 3. **Gold Layer（分析就绪层）**
- **目的**：存储业务就绪的分析数据，直接用于决策
- **格式**：Parquet 文件
- **处理内容**：
  - 基于业务规则筛选目标公司（公司评分 >= 0）
  - 基于条件筛选目标职位（学历、工作经验要求）
  - 数据关联和聚合
- **存储路径**：
  - `gold/target_company/dt=*/target_company.parquet`
  - `gold/target_JD/dt=*/target_JD.parquet`
- **特点**：
  - 业务就绪，可直接用于分析
  - 优化后的数据结构
  - 支持快速查询和报表生成

### 数据分区策略

- **分区键**：`dt=YYYYMMDD`（按日期分区）
- **优势**：
  - 支持增量处理
  - 便于数据管理和清理
  - 优化查询性能（分区裁剪）

---

## ⚡ 核心功能

### 1. **数据采集（Data Ingestion）**
- **LinkedIn 职位爬取**：使用 Selenium 自动化爬取 LinkedIn 职位信息
- **智能登录**：自动处理登录流程和验证
- **批量采集**：支持多页面、多关键词的批量数据采集
- **数据存储**：自动上传到 MinIO 对象存储

### 2. **数据处理（Data Processing）**
- **HTML 解析**：从原始 HTML 提取结构化数据（职位信息、公司信息、职位描述等）
- **并行处理**：使用 ThreadPoolExecutor 实现多线程并行处理，提升处理速度
- **数据清洗**：提取和标准化位置、时间、公司信息等字段

### 3. **智能分析（Intelligent Analysis）**
- **公司评估**：使用 LLM 对公司进行多维度评分
  - 公司规模（200-5000 人优先）
  - 所有权类型（非国有企业优先）
  - 行业类型（B2B/SaaS/企业服务优先）
  - 数据驱动文化（提及数据分析、BI 等关键词）
  - 企业文化（排除过于严格的等级制度）
  - 国际化程度（APAC/全球办公室优先）
- **职位描述分解**：使用 LLM 提取职位关键信息
  - 一句话描述
  - 关键词提取
  - 学历要求
  - 工作经验要求

### 4. **数据筛选（Data Filtering）**
- **目标公司筛选**：基于公司评分和业务规则筛选合适公司
- **目标职位筛选**：基于学历要求、工作经验等条件筛选职位
- **SQL 查询**：使用 DuckDB 进行复杂的数据关联和筛选

### 5. **数据查询与分析**
- **DuckDB SQL 查询**：支持标准 SQL 查询 Parquet 文件
- **Spark 集成**：支持大规模数据的分布式处理（可选）
- **Python 分析**：提供 Jupyter Notebook 进行数据探索和分析

---

## 🚀 快速开始

### 前置要求

- Docker & Docker Compose
- Python 3.8+
- Git

### 1. 克隆项目

```bash
git clone <repository-url>
cd Find_Job_Pipe_Line_V2
```

### 2. 启动服务

```bash
# 启动所有服务（Airflow, MinIO, Spark, PostgreSQL）
docker-compose up -d

# 或者只启动 MinIO
docker-compose up -d minio
```

### 3. 访问服务

- **Airflow Web UI**: http://localhost:8080
  - 默认用户名/密码: `airflow` / `airflow`
- **MinIO Console**: http://localhost:9001
  - 默认用户名/密码: `minioadmin` / `minioadmin`
- **Spark Master UI**: http://localhost:8086

### 4. 运行数据管道

#### 方式一：通过 Airflow UI

1. 登录 Airflow Web UI
2. 找到 `Linkedin_Scrape_dag` DAG，点击触发运行
3. 等待数据采集完成
4. 触发 `Data_Process_Pipeline` DAG 运行完整的数据处理流程

#### 方式二：直接运行 Python 脚本

```bash
# 数据采集
python dags/Linkedin_Scrape.py

# 数据处理（Raw to Bronze）
python dags/r2b_processing.py

# 公司评估（Bronze to Silver）
python dags/b2s_company_judgement.py

# 职位分解（Bronze to Silver）
python dags/b2s_JD_Decompose.py

# 目标公司筛选（Silver to Gold）
python dags/s2g_get_target_company.py

# 目标职位筛选（Silver to Gold）
python dags/s2g_get_target_JD.py
```

### 5. 查询数据

使用 DuckDB 查询 Parquet 文件：

```python
from Lib.exe_SQL import Exe_SQL

duckdb_engine = Exe_SQL()
duckdb_engine.connect()

# 查询目标公司
df_companies = duckdb_engine.execute_sql_file('read_target_company.sql')

# 查询目标职位
df_jobs = duckdb_engine.execute_sql_file('read_target_JD.sql')
```

---

## 📁 项目结构

```
Find_Job_Pipe_Line_V2/
├── dags/                          # Airflow DAGs
│   ├── Linkedin_Scrape.py        # LinkedIn 数据采集脚本
│   ├── Linkedin_Scrape_dag.py    # 数据采集 DAG
│   ├── Data_Process_Pipeline.py  # 主数据处理管道 DAG
│   ├── r2b_processing.py         # Raw to Bronze 处理
│   ├── b2s_company_judgement.py  # Bronze to Silver: 公司评估
│   ├── b2s_JD_Decompose.py       # Bronze to Silver: 职位分解
│   ├── s2g_get_target_company.py # Silver to Gold: 目标公司
│   └── s2g_get_target_JD.py      # Silver to Gold: 目标职位
│
├── Lib/                           # 核心库
│   ├── get_Linkedin.py           # LinkedIn 爬虫核心逻辑
│   ├── action.py                 # Selenium 驱动管理
│   ├── Html_Analist.py           # HTML 解析器
│   ├── LLM_Analysis.py           # LLM 分析接口
│   ├── exe_SQL.py                # DuckDB SQL 执行器
│   ├── Batch_Run.py              # 批量处理工具
│   └── SQL_script/               # SQL 查询脚本
│       ├── read_target_company.sql
│       └── read_target_JD.sql
│
├── Lab/                           # 实验和分析 Notebooks
│   ├── raw_data_process.ipynb   # 原始数据处理实验
│   ├── bronze_company_judgement.ipynb  # 公司评估实验
│   └── lakehouse_analysis_example.ipynb  # 数据湖分析示例
│
├── Prompts/                       # LLM 提示词配置
│   ├── company_judgement.yaml    # 公司评估提示词
│   └── JD_judgement.yaml         # 职位评估提示词
│
├── doc/                           # 项目文档
│   ├── Local_Lakehouse_Architecture.md  # 架构文档
│   ├── Local_Lakehouse_Quick_Start.md   # 快速开始指南
│   └── Spark_Integration_Guide.md       # Spark 集成指南
│
├── data/                          # 本地数据目录
├── logs/                          # Airflow 日志
├── docker-compose.yml             # Docker Compose 配置
└── README.md                      # 项目说明文档
```

---

## 🔄 数据管道

### 主数据管道（Data_Process_Pipeline）

```
r2b_data_process (Raw → Bronze)
    ↓
b2s_company_judgement (Bronze → Silver: 公司评估)
    ↓
b2s_JD_Decompose (Bronze → Silver: 职位分解)
    ↓
s2g_get_target_company (Silver → Gold: 目标公司)
    ↓
s2g_get_target_JD (Silver → Gold: 目标职位)
```

### 各阶段说明

#### 1. **r2b_data_process** (Raw to Bronze)
- **输入**：`raw/Linkedin_html/dt=YYYYMMDD/*.html`
- **处理**：
  - 从 MinIO 读取 HTML 文件
  - 使用 HTML 解析器提取结构化数据
  - 多线程并行处理（ThreadPoolExecutor，15 个工作线程）
- **输出**：`bronze/raw_json/dt=YYYYMMDD/*.json`
- **数据内容**：
  - 职位名称、职位 URL
  - 公司名称、公司 URL
  - 位置、发布时间
  - 职位描述内容
  - 公司信息内容

#### 2. **b2s_company_judgement** (Bronze to Silver: 公司评估)
- **输入**：`bronze/raw_json/dt=YYYYMMDD/*.json`
- **处理**：
  - 从 JSON 文件提取公司信息
  - 使用 LLM 进行多维度公司评估
  - 计算公司综合评分
- **输出**：`silver/company_info/dt=*/company_info_with_score.parquet`
- **评分维度**：
  - 公司规模（权重：3）
  - 所有权类型（权重：2）
  - 行业类型（权重：2）
  - 数据驱动提及（权重：3）
  - 企业文化（权重：1）
  - 国际化程度（权重：1）

#### 3. **b2s_JD_Decompose** (Bronze to Silver: 职位分解)
- **输入**：`bronze/raw_json/dt=YYYYMMDD/*.json`
- **处理**：
  - 提取职位描述内容
  - 使用 LLM 分解职位描述
  - 提取关键信息（关键词、学历要求、工作经验要求）
  - 多线程并行处理（16 个工作线程）
- **输出**：`silver/JD_Processed/dt=*/JD_Processed.parquet`
- **提取内容**：
  - 一句话描述
  - 关键词列表
  - 学历要求
  - 工作经验要求

#### 4. **s2g_get_target_company** (Silver to Gold: 目标公司)
- **输入**：`silver/company_info/dt=*/company_info_with_score.parquet`
- **处理**：
  - 使用 DuckDB 读取 Silver 层的公司信息
  - 基于公司评分进行筛选（`company_score >= 0`）
  - 聚合公司信息（按公司名称分组）
  - 计算加权综合评分
- **输出**：`gold/target_company/dt=YYYYMMDD/target_company.parquet`
- **筛选规则**：
  - 公司评分 >= 0
  - 排除公司信息为空的记录
  - 评分计算公式：`3×公司规模 + 2×所有权 + 2×行业 + 3×数据驱动提及 + 1×企业文化 + 1×国际化`

#### 5. **s2g_get_target_JD** (Silver to Gold: 目标职位)
- **输入**：
  - `gold/target_company/dt=*/target_company.parquet`
  - `silver/JD_Processed/dt=*/JD_Processed.parquet`
  - `bronze/raw_json/dt=YYYYMMDD/*.json`
- **处理**：
  - 使用 DuckDB 进行多表关联查询
  - 关联目标公司、职位描述和原始职位信息
  - 基于业务规则筛选目标职位
- **输出**：`gold/target_JD/dt=YYYYMMDD/target_JD.parquet`
- **筛选规则**：
  - 公司评分 >= 0
  - 学历要求：排除 `Master_above_or_elite_school`
  - 工作经验：排除 `3+_years`
  - 仅保留通过公司评估和职位评估的职位

---

## ✨ 设计亮点

### 1. **Medallion 架构实践**
- ✅ **三层数据分层**：Bronze/Silver/Gold 清晰的数据治理架构
- ✅ **Schema-on-Read**：灵活的数据结构，支持数据演进
- ✅ **数据可追溯性**：保留原始数据，支持数据回溯和重新处理
- ✅ **增量处理**：按日期分区，支持增量数据处理

### 2. **性能优化**
- ✅ **并行处理**：
  - HTML 解析：15 线程并行处理
  - LLM 分析：16 线程并行处理
  - 显著提升处理速度
- ✅ **列式存储**：使用 Parquet 格式，优化查询性能
- ✅ **分区裁剪**：按日期分区，支持查询优化

### 3. **智能化处理**
- ✅ **LLM 集成**：使用 DeepSeek API 进行智能分析
  - 公司多维度评估
  - 职位描述自动分解
- ✅ **可配置提示词**：使用 YAML 文件管理 LLM 提示词，便于调整和优化

### 4. **生产级设计**
- ✅ **容器化部署**：Docker Compose 一键启动所有服务
- ✅ **模块化代码**：清晰的代码结构，便于维护和扩展
- ✅ **错误处理**：完善的异常处理和日志记录
- ✅ **可扩展性**：支持 Spark 分布式处理，可处理大规模数据

### 5. **现代数据栈**
- ✅ **Airflow 编排**：可视化工作流管理，支持任务依赖和调度
- ✅ **MinIO 存储**：S3 兼容的对象存储，便于迁移到云环境
- ✅ **DuckDB 查询**：高性能 SQL 查询引擎，支持直接查询 Parquet
- ✅ **Spark 集成**：可选的大规模数据处理能力

### 6. **数据质量保证**
- ✅ **数据验证**：各层数据质量检查
- ✅ **数据清洗**：标准化和规范化处理
- ✅ **业务规则**：基于业务逻辑的数据筛选

---

## 📚 文档

### 核心文档
- [**Local_Lakehouse_Architecture.md**](doc/Local_Lakehouse_Architecture.md) - 详细的架构设计文档
- [**Local_Lakehouse_Quick_Start.md**](doc/Local_Lakehouse_Quick_Start.md) - 快速开始指南
- [**Lakehouse_Configuration_Guide.md**](doc/Lakehouse_Configuration_Guide.md) - 配置参考指南

### 技术文档
- [**Spark_Integration_Guide.md**](doc/Spark_Integration_Guide.md) - Spark 集成和使用指南
- [**MinIO_Python_Quick_Guide.md**](doc/MinIO_Python_Quick_Guide.md) - MinIO Python SDK 使用指南
- [**Lakehouse_vs_Traditional_DB_Comparison.md**](doc/Lakehouse_vs_Traditional_DB_Comparison.md) - 湖仓架构与传统数据库对比

### 操作文档
- [**如何在新文件夹创建Airflow流程.md**](doc/如何在新文件夹创建Airflow流程.md) - Airflow DAG 创建指南
- [**并行任务处理指南.md**](doc/并行任务处理指南.md) - 并行处理最佳实践
- [**README_SQL_Usage.md**](Lib/SQL_script/README_SQL_Usage.md) - SQL 脚本使用说明

---

## 🔧 配置说明

### 环境变量

创建 `.env` 文件（可选）：

```bash
# MinIO 配置
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=jobdatabucket

# Airflow 配置
AIRFLOW_UID=50000
AIRFLOW_WWW_USER_USERNAME=airflow
AIRFLOW_WWW_USER_PASSWORD=airflow

# LLM API 配置（在代码中配置）
DEEPSEEK_API_KEY=your_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com
```

### MinIO 配置

MinIO 服务默认配置：
- **API 端口**：9000
- **Console 端口**：9001
- **默认用户名/密码**：`minioadmin` / `minioadmin`
- **存储桶**：`jobdatabucket`

### Airflow 配置

Airflow 服务默认配置：
- **Web UI 端口**：8080
- **默认用户名/密码**：`airflow` / `airflow`
- **执行器**：LocalExecutor

---

## 🎓 技术亮点总结

### 架构设计能力
- ✅ 理解并实践 Medallion 架构（Bronze/Silver/Gold）
- ✅ 设计可扩展的数据管道架构
- ✅ 实现数据分层治理和 Schema-on-Read

### 数据工程能力
- ✅ 端到端数据管道构建（采集 → 存储 → 处理 → 分析）
- ✅ 大规模数据处理和性能优化
- ✅ 数据质量保证和验证

### 技术栈掌握
- ✅ **Airflow**：工作流编排和任务调度
- ✅ **MinIO/S3**：对象存储和数据湖实践
- ✅ **DuckDB**：高性能 SQL 查询引擎
- ✅ **Spark**：分布式计算（可选）
- ✅ **Parquet**：列式存储格式

### 智能化应用
- ✅ LLM 集成进行数据分析和提取
- ✅ 可配置的提示词管理
- ✅ 多维度数据评估

### 工程实践
- ✅ 容器化部署（Docker Compose）
- ✅ 模块化代码设计
- ✅ 完善的错误处理和日志
- ✅ 代码可维护性和可扩展性

---

## 🚧 未来规划

### 短期优化
- [ ] 添加数据质量监控和告警
- [ ] 优化 LLM 调用成本（批量处理、缓存）
- [ ] 添加数据血缘追踪
- [ ] 完善单元测试和集成测试

### 中期扩展
- [ ] 支持更多数据源（其他招聘网站）
- [ ] 添加实时数据处理能力（Kafka/Streaming）
- [ ] 构建数据可视化 Dashboard
- [ ] 添加更多机器学习模型（职位匹配推荐）

### 长期规划
- [ ] 迁移到云环境（AWS S3、EMR 等）
- [ ] 实现数据治理和元数据管理
- [ ] 构建数据产品 API
- [ ] 支持多租户和权限管理

---

## 📝 许可证

本项目为个人学习项目，仅供学习和参考使用。

---

## 👤 作者

**数据工程师 | 湖仓架构师**

> 这是一个展示端到端数据工程能力的实践项目，涵盖了从数据采集、存储、处理到分析的完整流程。项目采用现代数据栈和最佳实践，体现了对数据工程和湖仓架构的深入理解。

---

## 🙏 致谢

感谢以下开源项目和技术社区：
- [Apache Airflow](https://airflow.apache.org/)
- [MinIO](https://min.io/)
- [DuckDB](https://duckdb.org/)
- [Apache Spark](https://spark.apache.org/)
- [Selenium](https://www.selenium.dev/)

---

## 📧 联系方式

如有问题或建议，欢迎通过以下方式联系：
- GitHub Issues
- Email: [joeyclaire234@gmail.com]

---

**⭐ 如果这个项目对您有帮助，欢迎 Star 支持！**