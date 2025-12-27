# 湖仓文档阅读指南

## 文档概览与阅读顺序

### 📚 文档分类

#### 🟢 入门必读（按顺序）
1. **Local_Lakehouse_Quick_Start.md** - 快速开始
2. **Local_Lakehouse_Architecture.md** - 架构理解
3. **Lakehouse_Configuration_Guide.md** - 配置参考

#### 🟡 实践操作（边做边看）
4. **lakehouse_analysis_example.ipynb** - 查询示例
5. **parquet_io.py** - 代码参考（工具函数）

#### 🔵 进阶扩展（未来规划）
6. **Local_Lakehouse_PySpark_Design.md** - PySpark 集成（可选）

---

## 📖 各文档核心内容总结

### 1. Local_Lakehouse_Quick_Start.md ⭐ **最先读这个**

**核心内容：**
- ✅ 5 步快速上手流程
- ✅ 如何启动 MinIO
- ✅ 如何运行 DAG 处理数据
- ✅ 如何查询数据（3 种方法）
- ✅ 常见问题排查

**适合人群：** 所有用户（入门必读）

**阅读时间：** 10-15 分钟

**关键信息：**
```
1. 启动 MinIO: docker compose up -d minio
2. 触发 DAG: D2_Process_HTML_to_Lakehouse
3. 查询数据: 使用 DuckDB 或直接加载 DataFrame
```

---

### 2. Local_Lakehouse_Architecture.md ⭐ **理解架构**

**核心内容：**
- ✅ 三层数据分区（raw/staging/curated）
- ✅ 数据流转路径
- ✅ 文件命名规范
- ✅ 数据分区策略（按日期）

**适合人群：** 需要理解系统设计的用户

**阅读时间：** 15-20 分钟

**关键概念：**
```
raw/        → 原始 HTML 文件（不可变）
staging/    → 清洗后的 Parquet 表（可重新处理）
curated/    → 最终分析表（优化后的查询表）
```

**重点章节：**
- Data Zones（数据分区）- 理解三层架构
- Data Flow（数据流转）- 理解 ETL 流程
- Bucket Structure（存储结构）- 理解文件组织

---

### 3. Lakehouse_Configuration_Guide.md ⚙️ **配置参考**

**核心内容：**
- ✅ 环境变量配置
- ✅ MinIO 连接配置（容器内 vs 本地）
- ✅ 代码中的配置方式
- ✅ 路径辅助函数使用

**适合人群：** 需要配置或自定义的用户

**阅读时间：** 5-10 分钟

**关键信息：**
```python
# 容器内: minio:9000
# 本地: localhost:9000
# 环境变量: MINIO_ENDPOINT, MINIO_BUCKET 等
```

**使用场景：**
- 首次配置系统
- 修改连接参数
- 在不同环境运行代码

---

### 4. lakehouse_analysis_example.ipynb 💻 **实践操作**

**核心内容：**
- ✅ 4 种查询方法的完整示例
- ✅ 可直接运行的代码
- ✅ 从简单到复杂的查询示例

**适合人群：** 需要实际查询数据的用户

**阅读方式：** 在 Jupyter Notebook 中运行

**4 种方法：**
1. **直接加载 DataFrame** - 最简单
2. **DuckDB SQL 查询** - 单次查询
3. **注册表后查询** - 多次查询
4. **查询多个文件** - 跨日期查询

**使用建议：**
- 先运行第一个 cell（导入库）
- 按顺序运行每个示例
- 根据你的数据调整日期参数

---

### 5. parquet_io.py 📦 **代码工具参考**

**核心内容：**
- ✅ Parquet 文件读写函数
- ✅ MinIO 集成函数
- ✅ 函数 API 文档

**适合人群：** 需要编写自定义代码的开发者

**阅读方式：** 作为代码参考，需要时查阅

**主要函数：**
```python
# 保存到 MinIO
save_dataframe_to_minio(df, zone, table_name, date, filename)

# 从 MinIO 加载
load_dataframe_from_minio(zone, table_name, date, filename)

# 加载多个文件
load_dataframe_from_minio_prefix(zone, table_name, date=None)
```

**使用场景：**
- 编写自定义 ETL 脚本
- 需要批量处理数据
- 需要了解函数参数

---

### 6. Local_Lakehouse_PySpark_Design.md 🚀 **未来扩展（可选）**

**核心内容：**
- ✅ PySpark 与现有模块的集成点
- ✅ 何时使用 PySpark
- ✅ 架构演进路线图

**适合人群：** 计划扩展系统的用户

**阅读时间：** 10-15 分钟

**关键信息：**
- PySpark 可以替代 `Batch_Run.py` 的并发处理
- 可以用于大规模特征工程
- 与 MinIO + Parquet 完美集成

**阅读时机：**
- 数据量增长到需要分布式处理时
- 需要优化批处理性能时
- 计划引入 Spark 时

---

## 🎯 推荐阅读顺序

### 场景 1: 快速上手（第一次使用）

```
1. Local_Lakehouse_Quick_Start.md
   ↓ 跟着步骤操作
2. lakehouse_analysis_example.ipynb
   ↓ 运行示例代码
3. Local_Lakehouse_Architecture.md
   ↓ 理解为什么这样设计
```

**预计时间：** 30-45 分钟

---

### 场景 2: 深入理解（需要定制开发）

```
1. Local_Lakehouse_Quick_Start.md
   ↓ 了解基本流程
2. Local_Lakehouse_Architecture.md
   ↓ 理解架构设计
3. Lakehouse_Configuration_Guide.md
   ↓ 学习配置方法
4. parquet_io.py
   ↓ 查看工具函数 API
5. lakehouse_analysis_example.ipynb
   ↓ 实践查询操作
```

**预计时间：** 1-2 小时

---

### 场景 3: 系统规划（准备扩展）

```
1. Local_Lakehouse_Architecture.md
   ↓ 理解当前架构
2. Local_Lakehouse_PySpark_Design.md
   ↓ 了解扩展方向
3. Lakehouse_Configuration_Guide.md
   ↓ 规划配置方案
```

**预计时间：** 30-45 分钟

---

## 📋 快速查找表

| 我想... | 看哪个文档 | 重点章节 |
|---------|-----------|---------|
| **快速开始使用** | Quick_Start.md | Step 1-5 |
| **理解数据分区** | Architecture.md | Data Zones |
| **配置 MinIO** | Configuration_Guide.md | Environment Variables |
| **查询数据** | lakehouse_analysis_example.ipynb | Method 1-4 |
| **编写 ETL 代码** | parquet_io.py | save_dataframe_to_minio |
| **了解 PySpark 集成** | PySpark_Design.md | Section 2-3 |

---

## 🎓 学习路径建议

### 第 1 天：基础理解
- ✅ 阅读 Quick_Start.md
- ✅ 运行 DAG 处理数据
- ✅ 在 MinIO Console 查看数据

### 第 2 天：深入架构
- ✅ 阅读 Architecture.md
- ✅ 理解三层分区的作用
- ✅ 理解数据流转路径

### 第 3 天：实践查询
- ✅ 运行 lakehouse_analysis_example.ipynb
- ✅ 尝试修改查询条件
- ✅ 理解不同查询方法的区别

### 第 4 天：自定义开发
- ✅ 查看 parquet_io.py API
- ✅ 编写自定义处理脚本
- ✅ 参考 Configuration_Guide.md 配置环境

### 第 5 天：规划扩展（可选）
- ✅ 阅读 PySpark_Design.md
- ✅ 评估是否需要引入 Spark
- ✅ 规划系统演进路线

---

## 💡 关键概念速记

### 三层架构
```
raw/      → 原始数据（HTML/JSON）
staging/  → 清洗后的表（Parquet）
curated/  → 最终分析表（Parquet）
```

### 数据流转
```
HTML 文件 → DAG 处理 → raw/ → staging/ → curated/ → DuckDB 查询
```

### 关键工具
- **MinIO**: 对象存储（S3 兼容）
- **Parquet**: 列式存储格式
- **DuckDB**: 分析型查询引擎

---

## ❓ 常见问题

**Q: 我应该先读哪个？**
A: 如果是第一次使用，先读 `Quick_Start.md`，跟着步骤操作。

**Q: 代码看不懂怎么办？**
A: 先运行 `lakehouse_analysis_example.ipynb` 的示例，理解后再看 `parquet_io.py`。

**Q: 需要理解架构吗？**
A: 如果只是使用，Quick_Start 就够了。如果需要定制开发，建议读 Architecture.md。

**Q: PySpark 文档必须读吗？**
A: 不是必须的，这是未来扩展方向。只有计划引入 Spark 时才需要。

---

## 📝 总结

**最短路径（30 分钟）：**
1. Quick_Start.md → 跟着做
2. lakehouse_analysis_example.ipynb → 运行示例

**完整路径（2 小时）：**
1. Quick_Start.md
2. Architecture.md
3. Configuration_Guide.md
4. lakehouse_analysis_example.ipynb
5. parquet_io.py（需要时查阅）

**扩展路径（未来）：**
- PySpark_Design.md（需要时阅读）

---

**建议：从 Quick_Start.md 开始，边做边学！** 🚀

