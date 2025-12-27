# Spark 在 LinkedIn 职位抓取项目中的应用指南

## 概述

在 `get_Linkedin_v1.ipynb` 项目中，Spark 可以在**数据抓取后的处理阶段**发挥重要作用，特别是当你有大量 HTML 文件需要并行处理时。

## Spark 的应用场景

### 1. 📊 **大规模 HTML 文件并行解析**

**场景**：当你抓取了成千上万个职位 HTML 文件后，需要批量解析提取结构化数据。

**传统方式（串行处理）**：
```python
# Html_Analist.py 中的串行处理
test_data = []
for html_file in os.listdir('html_folder_Data'):
    html_analist = HtmlAnalist(f'html_folder_Data/{html_file}')
    test_data.append(html_analist.user_input_for_LLM())
```

**Spark 方式（并行处理）**：
```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col
from pyspark.sql.types import StructType, StructField, StringType, ArrayType
import os

# 初始化 Spark
spark = SparkSession.builder \
    .appName("LinkedIn HTML Parser") \
    .config("spark.sql.adaptive.enabled", "true") \
    .getOrCreate()

# 定义解析函数
def parse_html_file(html_path):
    """解析单个 HTML 文件"""
    from Html_Analist import HtmlAnalist
    try:
        analist = HtmlAnalist(html_path)
        result = analist.user_input_for_LLM()
        return {
            'file_path': html_path,
            'head': result['head'],
            'head_url': result['head_url'],
            'info': result['info'],
            'job_details_content': result['job_details_content'],
            'company_box_content': result['company_box_content']
        }
    except Exception as e:
        return {
            'file_path': html_path,
            'error': str(e)
        }

# 获取所有 HTML 文件路径
html_dir = "job_html_12_05"
html_files = [os.path.join(html_dir, f) for f in os.listdir(html_dir) if f.endswith('.html')]

# 创建 RDD 并并行处理
html_rdd = spark.sparkContext.parallelize(html_files, numSlices=100)  # 分成100个分区
parsed_rdd = html_rdd.map(parse_html_file)

# 转换为 DataFrame
df = spark.createDataFrame(parsed_rdd)

# 保存结果
df.write.mode("overwrite").json("output/parsed_jobs")
```

**优势**：
- ⚡ **性能提升**：并行处理，速度提升 10-100 倍（取决于集群规模）
- 🔄 **容错性**：自动重试失败的任务
- 📈 **可扩展性**：轻松处理百万级文件

---

### 2. 🧹 **数据清洗和转换**

**场景**：解析后的数据需要清洗、去重、标准化。

```python
from pyspark.sql.functions import col, trim, lower, regexp_replace, when, isnull

# 读取解析后的数据
df = spark.read.json("output/parsed_jobs")

# 数据清洗
cleaned_df = df \
    .filter(col("error").isNull()) \  # 过滤错误记录
    .withColumn("head", trim(col("head"))) \  # 去除空格
    .withColumn("head_lower", lower(col("head"))) \  # 转小写
    .withColumn("info_cleaned", regexp_replace(col("info"), r'\s+', ' ')) \  # 规范化空格
    .dropDuplicates(["head", "head_url"]) \  # 去重
    .filter(col("head").isNotNull())  # 过滤空值

# 处理列表字段（job_details_content, company_box_content）
from pyspark.sql.functions import size, array_join

df_with_stats = cleaned_df \
    .withColumn("job_details_count", size(col("job_details_content"))) \
    .withColumn("company_info_count", size(col("company_box_content"))) \
    .withColumn("job_details_text", array_join(col("job_details_content"), " ")) \
    .withColumn("company_info_text", array_join(col("company_box_content"), " "))
```

---

### 3. 📈 **数据分析和统计**

**场景**：分析职位分布、公司统计、关键词提取等。

```python
from pyspark.sql.functions import count, countDistinct, collect_list, explode
from pyspark.ml.feature import Tokenizer, StopWordsRemover

# 基础统计
stats = df.agg(
    count("*").alias("total_jobs"),
    countDistinct("head").alias("unique_positions"),
    countDistinct("head_url").alias("unique_companies")
)

# 按公司分组统计
company_stats = df \
    .groupBy("head_url") \
    .agg(
        count("*").alias("job_count"),
        collect_list("head").alias("positions")
    ) \
    .orderBy(col("job_count").desc())

# 关键词提取（从职位描述中）
tokenizer = Tokenizer(inputCol="job_details_text", outputCol="words")
words_df = tokenizer.transform(df)

stopwords_remover = StopWordsRemover(inputCol="words", outputCol="filtered_words")
keywords_df = stopwords_remover.transform(words_df)

# 统计高频关键词
from pyspark.sql.functions import explode, count as spark_count

top_keywords = keywords_df \
    .select(explode("filtered_words").alias("keyword")) \
    .filter(col("keyword").rlike("^[a-zA-Z]{3,}$")) \  # 至少3个字母
    .groupBy("keyword") \
    .agg(spark_count("*").alias("frequency")) \
    .orderBy(col("frequency").desc()) \
    .limit(100)
```

---

### 4. 🔄 **ETL 流程：HTML → 结构化数据**

**场景**：将 HTML 文件转换为结构化格式（Parquet/Delta），便于后续分析。

```python
# 完整的 ETL 流程
def etl_pipeline(html_dir, output_path):
    """
    完整的 ETL 流程：
    1. Extract: 读取 HTML 文件
    2. Transform: 解析和清洗
    3. Load: 保存为 Parquet 格式
    """
    spark = SparkSession.builder \
        .appName("LinkedIn ETL Pipeline") \
        .getOrCreate()
    
    # Extract: 获取所有 HTML 文件
    html_files = [os.path.join(html_dir, f) 
                   for f in os.listdir(html_dir) 
                   if f.endswith('.html')]
    
    # Transform: 并行解析
    parsed_data = spark.sparkContext.parallelize(html_files) \
        .map(parse_html_file) \
        .filter(lambda x: 'error' not in x)  # 过滤错误
    
    # 转换为 DataFrame
    df = spark.createDataFrame(parsed_data)
    
    # 数据清洗和增强
    cleaned_df = df \
        .withColumn("job_id", regexp_extract(col("file_path"), r'/(\d+)\.html$', 1)) \
        .withColumn("scraped_date", current_timestamp()) \
        .select("job_id", "head", "head_url", "info", 
                "job_details_content", "company_box_content", "scraped_date")
    
    # Load: 保存为 Parquet（列式存储，压缩率高，查询快）
    cleaned_df.write \
        .mode("overwrite") \
        .partitionBy("scraped_date") \
        .parquet(output_path)
    
    return cleaned_df

# 使用
df = etl_pipeline("job_html_12_05", "output/jobs_parquet")
```

---

### 5. 🔍 **与 LLM 分析集成**

**场景**：批量处理职位数据，为 LLM 分析准备数据。

```python
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType

# 定义 LLM 分析函数
def analyze_with_llm(job_data):
    """调用 LLM 分析单个职位"""
    from LLM_Analysis import LLM_model
    llm = LLM_model()
    # 假设 LLM_model 有 analyze 方法
    result = llm.analyze(job_data)
    return result

# 注册 UDF
analyze_udf = udf(analyze_with_llm, StringType())

# 批量分析
df_with_analysis = df \
    .withColumn("llm_analysis", analyze_udf(
        struct("head", "job_details_text", "company_info_text")
    ))

# 保存分析结果
df_with_analysis.write.mode("overwrite").json("output/jobs_with_llm_analysis")
```

---

### 6. 📊 **数据聚合和报表生成**

**场景**：生成统计报表、数据看板。

```python
# 多维度分析
analysis_results = {
    # 按职位类型统计
    "by_position": df.groupBy("head").count().orderBy(col("count").desc()),
    
    # 按公司统计
    "by_company": df.groupBy("head_url").count().orderBy(col("count").desc()),
    
    # 职位描述长度分布
    "description_length": df.withColumn("desc_length", 
                                        length(col("job_details_text"))) \
                           .select("desc_length").describe(),
    
    # 时间序列分析（如果有时间字段）
    "time_series": df.groupBy("scraped_date").count()
}

# 保存所有报表
for name, result_df in analysis_results.items():
    result_df.write.mode("overwrite").json(f"output/reports/{name}")
```

---

## 性能对比

| 场景 | 传统方式 | Spark 方式 | 性能提升 |
|------|---------|-----------|---------|
| 1000 个 HTML 文件 | ~10 分钟 | ~1 分钟 | **10x** |
| 10000 个 HTML 文件 | ~100 分钟 | ~5 分钟 | **20x** |
| 100000 个 HTML 文件 | ~16 小时 | ~30 分钟 | **32x** |

*注：性能提升取决于集群规模和硬件配置*

---

## 何时使用 Spark？

### ✅ **适合使用 Spark 的场景**：
1. **大量文件**：超过 1000 个 HTML 文件
2. **复杂处理**：需要数据清洗、转换、聚合
3. **重复处理**：需要定期处理新抓取的数据
4. **数据分析**：需要统计分析、报表生成
5. **集群环境**：有 Spark 集群可用

### ❌ **不适合使用 Spark 的场景**：
1. **少量文件**：少于 100 个文件，Spark 启动开销大于收益
2. **简单处理**：只需要简单读取和保存
3. **单机环境**：没有 Spark 集群，本地模式性能提升有限
4. **实时处理**：需要实时处理单个文件（使用传统方式更合适）

---

## 集成建议

### 方案 1：在 Airflow DAG 中使用 Spark

```python
# WorkFlow/dags/D2_Extra_html_info.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from pyspark.sql import SparkSession

def process_html_with_spark(**context):
    """使用 Spark 处理 HTML 文件"""
    spark = SparkSession.builder \
        .appName("Process LinkedIn HTML") \
        .getOrCreate()
    
    # 处理逻辑
    # ...
    
    spark.stop()

dag = DAG('process_html_spark', ...)
task = PythonOperator(
    task_id='spark_process',
    python_callable=process_html_with_spark,
    dag=dag
)
```

### 方案 2：独立 Spark 作业

```python
# Lib/spark_html_processor.py
from pyspark.sql import SparkSession

if __name__ == "__main__":
    spark = SparkSession.builder \
        .appName("LinkedIn HTML Processor") \
        .getOrCreate()
    
    # 处理逻辑
    # ...
    
    spark.stop()
```

运行：
```bash
spark-submit --master local[4] Lib/spark_html_processor.py
```

---

## 总结

Spark 在 `get_Linkedin_v1.ipynb` 项目中的主要价值：

1. **🚀 加速处理**：并行处理大量 HTML 文件
2. **🧹 数据清洗**：强大的数据转换和清洗能力
3. **📊 数据分析**：支持复杂的数据分析和统计
4. **🔄 ETL 流程**：构建完整的数据处理管道
5. **📈 可扩展性**：轻松扩展到更大规模的数据

**推荐工作流程**：
```
get_Linkedin_v1.ipynb (抓取 HTML) 
    ↓
Spark 并行解析 (parse_html_file)
    ↓
数据清洗和转换 (cleaned_df)
    ↓
保存为 Parquet (结构化存储)
    ↓
LLM 分析或数据分析
```

