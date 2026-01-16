# 🎯 Intelligent Job Pipeline - Data Engineering Project
@

[English](README_EN.md) | [中文](README.md)

> An end-to-end data engineering practice project based on Lakehouse architecture, implementing a complete data pipeline from LinkedIn job data collection, processing, analysis to intelligent filtering.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Airflow](https://img.shields.io/badge/Airflow-2.8.0-orange.svg)](https://airflow.apache.org/)
[![MinIO](https://img.shields.io/badge/MinIO-S3--compatible-green.svg)](https://min.io/)
[![DuckDB](https://img.shields.io/badge/DuckDB-Analytics-yellow.svg)](https://duckdb.org/)
[![Spark](https://img.shields.io/badge/Spark-3.5.7-red.svg)](https://spark.apache.org/)

---

## 📋 Table of Contents

- [Project Overview](#-project-overview)
- [System Architecture](#️-system-architecture)
- [Tech Stack](#️-tech-stack)
- [Data Architecture](#-data-architecture)
- [Core Features](#-core-features)
- [Quick Start](#-quick-start)
- [Project Structure](#-project-structure)
- [Data Pipeline](#-data-pipeline)
- [Design Highlights](#-design-highlights)
- [Documentation](#-documentation)

---

## 🎯 Project Overview

This is a **production-grade data engineering practice project** that demonstrates end-to-end data pipeline capabilities from data collection to intelligent analysis. The project adopts the **Medallion Architecture** (Bronze/Silver/Gold three-layer data partitioning) and combines modern data stack technologies to implement automated collection, processing, analysis, and intelligent filtering of LinkedIn job data.

### Core Value

- ✅ **End-to-End Data Engineering**: Complete workflow from web scraping to data storage, processing, and analysis
- ✅ **Lakehouse Architecture Practice**: Adopts Medallion architecture for data governance and Schema-on-Read
- ✅ **Modern Data Stack**: Integrates mainstream data tools like Airflow, MinIO, DuckDB, Spark
- ✅ **Intelligent Processing**: Integrates LLM for company evaluation and job description decomposition
- ✅ **Production-Grade Design**: Containerized deployment, modular code, scalable architecture

---

## 🏗️ System Architecture

### Overall Architecture Diagram

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

### Data Flow

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

## 🛠️ Tech Stack

### Data Orchestration
- **Apache Airflow 2.8.0** - Workflow orchestration and task scheduling

### Data Storage
- **MinIO** - S3-compatible object storage, serving as the data lake storage layer
- **Parquet** - Columnar storage format for optimized query performance

### Compute Engines
- **DuckDB** - High-performance analytical database for SQL queries and data analysis
- **Apache Spark 3.5.7** - Distributed computing engine (optional, for large-scale data processing)

### Data Collection
- **Selenium** - Web automation for LinkedIn job data scraping
- **BeautifulSoup** - HTML parsing

### Data Processing
- **Python 3.8+** - Primary programming language
- **Pandas** - Data processing and analysis
- **PyArrow** - Parquet file I/O

### AI/LLM Integration
- **DeepSeek API** - LLM service for company evaluation and job description decomposition

### Containerization
- **Docker & Docker Compose** - Containerized deployment

---

## 📊 Data Architecture

### Medallion Architecture (Three-Layer Data Partitioning)

This project adopts the **Medallion Architecture**, which is a best practice for modern data lakehouse architecture:

#### 1. **Bronze Layer (Raw Data Layer)**
- **Purpose**: Store raw, unprocessed data as the source of truth
- **Format**: JSON files
- **Data Source**: Structured JSON from HTML parsing
- **Storage Path**: `bronze/raw_json/dt=YYYYMMDD/*.json`
- **Characteristics**:
  - Preserves original data, supports data backtracking
  - Partitioned by date for easy data management
  - Immutable data

#### 2. **Silver Layer (Cleaned Data Layer)**
- **Purpose**: Store cleaned, standardized, and enriched data
- **Format**: Parquet files
- **Processing Content**:
  - Company information evaluation (multi-dimensional scoring using LLM)
  - Job description decomposition (extracting keywords, education requirements, work experience, etc.)
- **Storage Paths**:
  - `silver/company_info/dt=*/company_info_with_score.parquet`
  - `silver/JD_Processed/dt=*/JD_Processed.parquet`
- **Characteristics**:
  - Structured data for easy querying
  - Columnar storage for optimized query performance
  - Supports data quality checks

#### 3. **Gold Layer (Analytical Ready Layer)**
- **Purpose**: Store business-ready analytical data for direct decision-making
- **Format**: Parquet files
- **Processing Content**:
  - Filter target companies based on business rules (company score >= 0)
  - Filter target positions based on conditions (education, work experience requirements)
  - Data joins and aggregations
- **Storage Paths**:
  - `gold/target_company/dt=*/target_company.parquet`
  - `gold/target_JD/dt=*/target_JD.parquet`
- **Characteristics**:
  - Business-ready, directly usable for analysis
  - Optimized data structure
  - Supports fast queries and report generation

### Data Partitioning Strategy

- **Partition Key**: `dt=YYYYMMDD` (partitioned by date)
- **Advantages**:
  - Supports incremental processing
  - Facilitates data management and cleanup
  - Optimizes query performance (partition pruning)

---

## ⚡ Core Features

### 1. **Data Ingestion**
- **LinkedIn Job Scraping**: Automated scraping of LinkedIn job information using Selenium
- **Smart Login**: Automatic handling of login flow and verification
- **Batch Collection**: Supports batch data collection across multiple pages and keywords
- **Data Storage**: Automatic upload to MinIO object storage

### 2. **Data Processing**
- **HTML Parsing**: Extract structured data from raw HTML (job information, company information, job descriptions, etc.)
- **Parallel Processing**: Multi-threaded parallel processing using ThreadPoolExecutor for improved speed
- **Data Cleaning**: Extract and standardize fields like location, time, company information

### 3. **Intelligent Analysis**
- **Company Evaluation**: Multi-dimensional company scoring using LLM
  - Company size (200-5000 employees preferred)
  - Ownership type (non-state-owned enterprises preferred)
  - Industry type (B2B/SaaS/enterprise services preferred)
  - Data-driven culture (mentions of data analysis, BI, etc.)
  - Corporate culture (excludes overly strict hierarchy)
  - International presence (APAC/global offices preferred)
- **Job Description Decomposition**: Extract key job information using LLM
  - One-sentence description
  - Keyword extraction
  - Education requirements
  - Work experience requirements

### 4. **Data Filtering**
- **Target Company Filtering**: Filter suitable companies based on company scores and business rules
- **Target Position Filtering**: Filter positions based on education requirements, work experience, etc.
- **SQL Queries**: Use DuckDB for complex data joins and filtering

### 5. **Data Query & Analysis**
- **DuckDB SQL Queries**: Support standard SQL queries on Parquet files
- **Spark Integration**: Support distributed processing for large-scale data (optional)
- **Python Analysis**: Provide Jupyter Notebooks for data exploration and analysis

---

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.8+
- Git

### 1. Clone the Project

```bash
git clone <repository-url>
cd Find_Job_Pipe_Line_V2
```

### 2. Start Services

```bash
# Start all services (Airflow, MinIO, Spark, PostgreSQL)
docker-compose up -d

# Or start only MinIO
docker-compose up -d minio
```

### 3. Access Services

- **Airflow Web UI**: http://localhost:8080
  - Default username/password: `airflow` / `airflow`
- **MinIO Console**: http://localhost:9001
  - Default username/password: `minioadmin` / `minioadmin`
- **Spark Master UI**: http://localhost:8086

### 4. Run Data Pipeline

#### Method 1: Through Airflow UI

1. Log in to Airflow Web UI
2. Find the `Linkedin_Scrape_dag` DAG and trigger it
3. Wait for data collection to complete
4. Trigger the `Data_Process_Pipeline` DAG to run the complete data processing workflow

#### Method 2: Run Python Scripts Directly

```bash
# Data collection
python dags/Linkedin_Scrape.py

# Data processing (Raw to Bronze)
python dags/r2b_processing.py

# Company evaluation (Bronze to Silver)
python dags/b2s_company_judgement.py

# Job decomposition (Bronze to Silver)
python dags/b2s_JD_Decompose.py

# Target company filtering (Silver to Gold)
python dags/s2g_get_target_company.py

# Target position filtering (Silver to Gold)
python dags/s2g_get_target_JD.py
```

### 5. Query Data

Use DuckDB to query Parquet files:

```python
from Lib.exe_SQL import Exe_SQL

duckdb_engine = Exe_SQL()
duckdb_engine.connect()

# Query target companies
df_companies = duckdb_engine.execute_sql_file('read_target_company.sql')

# Query target positions
df_jobs = duckdb_engine.execute_sql_file('read_target_JD.sql')
```

---

## 📁 Project Structure

```
Find_Job_Pipe_Line_V2/
├── dags/                          # Airflow DAGs
│   ├── Linkedin_Scrape.py        # LinkedIn data collection script
│   ├── Linkedin_Scrape_dag.py    # Data collection DAG
│   ├── Data_Process_Pipeline.py  # Main data processing pipeline DAG
│   ├── r2b_processing.py         # Raw to Bronze processing
│   ├── b2s_company_judgement.py  # Bronze to Silver: Company evaluation
│   ├── b2s_JD_Decompose.py       # Bronze to Silver: Job decomposition
│   ├── s2g_get_target_company.py # Silver to Gold: Target companies
│   └── s2g_get_target_JD.py      # Silver to Gold: Target positions
│
├── Lib/                           # Core libraries
│   ├── get_Linkedin.py           # LinkedIn scraper core logic
│   ├── action.py                 # Selenium driver management
│   ├── Html_Analist.py           # HTML parser
│   ├── LLM_Analysis.py           # LLM analysis interface
│   ├── exe_SQL.py                # DuckDB SQL executor
│   ├── Batch_Run.py              # Batch processing utilities
│   └── SQL_script/               # SQL query scripts
│       ├── read_target_company.sql
│       └── read_target_JD.sql
│
├── Lab/                           # Experimental and analysis notebooks
│   ├── raw_data_process.ipynb   # Raw data processing experiments
│   ├── bronze_company_judgement.ipynb  # Company evaluation experiments
│   └── lakehouse_analysis_example.ipynb  # Data lake analysis examples
│
├── Prompts/                       # LLM prompt configurations
│   ├── company_judgement.yaml    # Company evaluation prompts
│   └── JD_judgement.yaml         # Job evaluation prompts
│
├── doc/                           # Project documentation
│   ├── Local_Lakehouse_Architecture.md  # Architecture documentation
│   ├── Local_Lakehouse_Quick_Start.md   # Quick start guide
│   └── Spark_Integration_Guide.md       # Spark integration guide
│
├── data/                          # Local data directory
├── logs/                          # Airflow logs
├── docker-compose.yml             # Docker Compose configuration
└── README.md                      # Project documentation
```

---

## 🔄 Data Pipeline

### Main Data Pipeline (Data_Process_Pipeline)

```
r2b_data_process (Raw → Bronze)
    ↓
b2s_company_judgement (Bronze → Silver: Company Evaluation)
    ↓
b2s_JD_Decompose (Bronze → Silver: Job Decomposition)
    ↓
s2g_get_target_company (Silver → Gold: Target Companies)
    ↓
s2g_get_target_JD (Silver → Gold: Target Positions)
```

### Stage Descriptions

#### 1. **r2b_data_process** (Raw to Bronze)
- **Input**: `raw/Linkedin_html/dt=YYYYMMDD/*.html`
- **Processing**:
  - Read HTML files from MinIO
  - Extract structured data using HTML parser
  - Multi-threaded parallel processing (ThreadPoolExecutor, 15 worker threads)
- **Output**: `bronze/raw_json/dt=YYYYMMDD/*.json`
- **Data Content**:
  - Job name, job URL
  - Company name, company URL
  - Location, publication time
  - Job description content
  - Company information content

#### 2. **b2s_company_judgement** (Bronze to Silver: Company Evaluation)
- **Input**: `bronze/raw_json/dt=YYYYMMDD/*.json`
- **Processing**:
  - Extract company information from JSON files
  - Multi-dimensional company evaluation using LLM
  - Calculate comprehensive company score
- **Output**: `silver/company_info/dt=*/company_info_with_score.parquet`
- **Scoring Dimensions**:
  - Company size (weight: 3)
  - Ownership type (weight: 2)
  - Industry type (weight: 2)
  - Data-driven mentions (weight: 3)
  - Corporate culture (weight: 1)
  - International presence (weight: 1)

#### 3. **b2s_JD_Decompose** (Bronze to Silver: Job Decomposition)
- **Input**: `bronze/raw_json/dt=YYYYMMDD/*.json`
- **Processing**:
  - Extract job description content
  - Decompose job description using LLM
  - Extract key information (keywords, education requirements, work experience requirements)
  - Multi-threaded parallel processing (16 worker threads)
- **Output**: `silver/JD_Processed/dt=*/JD_Processed.parquet`
- **Extracted Content**:
  - One-sentence description
  - Keyword list
  - Education requirements
  - Work experience requirements

#### 4. **s2g_get_target_company** (Silver to Gold: Target Companies)
- **Input**: `silver/company_info/dt=*/company_info_with_score.parquet`
- **Processing**:
  - Read company information from Silver layer using DuckDB
  - Filter based on company score (`company_score >= 0`)
  - Aggregate company information (group by company name)
  - Calculate weighted comprehensive score
- **Output**: `gold/target_company/dt=YYYYMMDD/target_company.parquet`
- **Filtering Rules**:
  - Company score >= 0
  - Exclude records with null company information
  - Score calculation formula: `3×company_size + 2×ownership + 2×industry + 3×data_driven_mentions + 1×culture + 1×international`

#### 5. **s2g_get_target_JD** (Silver to Gold: Target Positions)
- **Input**:
  - `gold/target_company/dt=*/target_company.parquet`
  - `silver/JD_Processed/dt=*/JD_Processed.parquet`
  - `bronze/raw_json/dt=YYYYMMDD/*.json`
- **Processing**:
  - Multi-table join queries using DuckDB
  - Join target companies, job descriptions, and original job information
  - Filter target positions based on business rules
- **Output**: `gold/target_JD/dt=YYYYMMDD/target_JD.parquet`
- **Filtering Rules**:
  - Company score >= 0
  - Education requirement: Exclude `Master_above_or_elite_school`
  - Work experience: Exclude `3+_years`
  - Only retain positions that pass both company and job evaluation

---

## ✨ Design Highlights

### 1. **Medallion Architecture Practice**
- ✅ **Three-Layer Data Partitioning**: Clear data governance architecture with Bronze/Silver/Gold
- ✅ **Schema-on-Read**: Flexible data structure supporting data evolution
- ✅ **Data Traceability**: Preserve raw data, support data backtracking and reprocessing
- ✅ **Incremental Processing**: Date-based partitioning supports incremental data processing

### 2. **Performance Optimization**
- ✅ **Parallel Processing**:
  - HTML parsing: 15-thread parallel processing
  - LLM analysis: 16-thread parallel processing
  - Significantly improves processing speed
- ✅ **Columnar Storage**: Use Parquet format for optimized query performance
- ✅ **Partition Pruning**: Date-based partitioning supports query optimization

### 3. **Intelligent Processing**
- ✅ **LLM Integration**: Use DeepSeek API for intelligent analysis
  - Multi-dimensional company evaluation
  - Automatic job description decomposition
- ✅ **Configurable Prompts**: Use YAML files to manage LLM prompts for easy adjustment and optimization

### 4. **Production-Grade Design**
- ✅ **Containerized Deployment**: Docker Compose one-click startup for all services
- ✅ **Modular Code**: Clear code structure for easy maintenance and extension
- ✅ **Error Handling**: Comprehensive exception handling and logging
- ✅ **Scalability**: Support Spark distributed processing for large-scale data

### 5. **Modern Data Stack**
- ✅ **Airflow Orchestration**: Visual workflow management with task dependencies and scheduling
- ✅ **MinIO Storage**: S3-compatible object storage, easy migration to cloud environments
- ✅ **DuckDB Queries**: High-performance SQL query engine supporting direct Parquet queries
- ✅ **Spark Integration**: Optional large-scale data processing capabilities

### 6. **Data Quality Assurance**
- ✅ **Data Validation**: Data quality checks at each layer
- ✅ **Data Cleaning**: Standardization and normalization processing
- ✅ **Business Rules**: Data filtering based on business logic

---

## 📚 Documentation

### Core Documentation
- [**Local_Lakehouse_Architecture.md**](doc/Local_Lakehouse_Architecture.md) - Detailed architecture design documentation
- [**Local_Lakehouse_Quick_Start.md**](doc/Local_Lakehouse_Quick_Start.md) - Quick start guide
- [**Lakehouse_Configuration_Guide.md**](doc/Lakehouse_Configuration_Guide.md) - Configuration reference guide

### Technical Documentation
- [**Spark_Integration_Guide.md**](doc/Spark_Integration_Guide.md) - Spark integration and usage guide
- [**MinIO_Python_Quick_Guide.md**](doc/MinIO_Python_Quick_Guide.md) - MinIO Python SDK usage guide
- [**Lakehouse_vs_Traditional_DB_Comparison.md**](doc/Lakehouse_vs_Traditional_DB_Comparison.md) - Lakehouse architecture vs traditional database comparison

### Operational Documentation
- [**如何在新文件夹创建Airflow流程.md**](doc/如何在新文件夹创建Airflow流程.md) - Airflow DAG creation guide
- [**并行任务处理指南.md**](doc/并行任务处理指南.md) - Parallel processing best practices
- [**README_SQL_Usage.md**](Lib/SQL_script/README_SQL_Usage.md) - SQL script usage instructions

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file (optional):

```bash
# MinIO Configuration
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=jobdatabucket

# Airflow Configuration
AIRFLOW_UID=50000
AIRFLOW_WWW_USER_USERNAME=airflow
AIRFLOW_WWW_USER_PASSWORD=airflow

# LLM API Configuration (configure in code)
DEEPSEEK_API_KEY=your_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com
```

### MinIO Configuration

MinIO service default configuration:
- **API Port**: 9000
- **Console Port**: 9001
- **Default Username/Password**: `minioadmin` / `minioadmin`
- **Storage Bucket**: `jobdatabucket`

### Airflow Configuration

Airflow service default configuration:
- **Web UI Port**: 8080
- **Default Username/Password**: `airflow` / `airflow`
- **Executor**: LocalExecutor

---

## 🎓 Technical Highlights Summary

### Architecture Design Capabilities
- ✅ Understanding and practice of Medallion Architecture (Bronze/Silver/Gold)
- ✅ Design scalable data pipeline architecture
- ✅ Implement data layer governance and Schema-on-Read

### Data Engineering Capabilities
- ✅ End-to-end data pipeline construction (Collection → Storage → Processing → Analysis)
- ✅ Large-scale data processing and performance optimization
- ✅ Data quality assurance and validation

### Technology Stack Mastery
- ✅ **Airflow**: Workflow orchestration and task scheduling
- ✅ **MinIO/S3**: Object storage and data lake practice
- ✅ **DuckDB**: High-performance SQL query engine
- ✅ **Spark**: Distributed computing (optional)
- ✅ **Parquet**: Columnar storage format

### Intelligent Applications
- ✅ LLM integration for data analysis and extraction
- ✅ Configurable prompt management
- ✅ Multi-dimensional data evaluation

### Engineering Practices
- ✅ Containerized deployment (Docker Compose)
- ✅ Modular code design
- ✅ Comprehensive error handling and logging
- ✅ Code maintainability and extensibility

---

## 🚧 Future Roadmap

### Short-term Optimizations
- [ ] Add data quality monitoring and alerts
- [ ] Optimize LLM call costs (batch processing, caching)
- [ ] Add data lineage tracking
- [ ] Improve unit tests and integration tests

### Mid-term Extensions
- [ ] Support more data sources (other job websites)
- [ ] Add real-time data processing capabilities (Kafka/Streaming)
- [ ] Build data visualization Dashboard
- [ ] Add machine learning models (job matching recommendations)

### Long-term Planning
- [ ] Migrate to cloud environment (AWS S3, EMR, etc.)
- [ ] Implement data governance and metadata management
- [ ] Build data product API
- [ ] Support multi-tenant and permission management

---

## 📝 License

This project is a personal learning project, for learning and reference purposes only.

---

## 👤 Author

**Data Engineer | Lakehouse Architect**

> This is a practice project demonstrating end-to-end data engineering capabilities, covering the complete workflow from data collection, storage, processing to analysis. The project adopts modern data stack and best practices, reflecting deep understanding of data engineering and lakehouse architecture.

---

## 🙏 Acknowledgments

Thanks to the following open-source projects and technical communities:
- [Apache Airflow](https://airflow.apache.org/)
- [MinIO](https://min.io/)
- [DuckDB](https://duckdb.org/)
- [Apache Spark](https://spark.apache.org/)
- [Selenium](https://www.selenium.dev/)

---

## 📧 Contact

For questions or suggestions, please contact us through:
- GitHub Issues
- Email: [your-email@example.com]

---

**⭐ If this project is helpful to you, please consider giving it a Star!**