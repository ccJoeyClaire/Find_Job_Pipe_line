# 快速开始：让 Airflow 执行本地代码

## ✅ 是的，可以让 Airflow 执行本地代码！

通过 HTTP 服务的方式，实现 Airflow（Docker）和本地代码（Windows）的分离。

---

## 🚀 3 步快速开始

### 步骤 1: 安装依赖并启动本地服务

```bash
# 安装依赖
pip install fastapi uvicorn

# 启动服务（在项目根目录）
python local_scraper_service.py
```

服务启动后会显示：
```
Starting Local Scraper Service...
Service will be available at: http://localhost:8000
```

### 步骤 2: 配置 Airflow Connection

1. 打开 Airflow UI: http://localhost:8080
2. 进入 **Admin → Connections**
3. 点击 **+** 添加连接
4. 填写：
   - **Connection Id**: `local_scraper_service`
   - **Connection Type**: `HTTP`
   - **Host**: `host.docker.internal`
   - **Port**: `8000`
   - **Schema**: `http`

### 步骤 3: 使用新的 DAG

1. 在 Airflow UI 中刷新 DAG 列表
2. 找到 `D1_Web_Scrape_Local`
3. 启用并触发

---

## 📋 文件说明

| 文件 | 说明 |
|------|------|
| `local_scraper_service.py` | 本地 HTTP 服务（在 Windows 上运行） |
| `WorkFlow/dags/D1_Web_Scrape_Local.py` | 新的 DAG（使用 HTTP 触发） |
| `WorkFlow/LOCAL_EXECUTION_GUIDE.md` | 详细方案对比 |
| `WorkFlow/LOCAL_SERVICE_SETUP.md` | 设置和故障排除指南 |

---

## 🎯 工作原理

```
┌─────────────────────┐
│  Airflow (Docker)   │
│  ┌───────────────┐  │
│  │ 调度和编排     │  │
│  │ 发送 HTTP 请求 │  │
│  └───────────────┘  │
└──────────┬──────────┘
           │ HTTP POST
           ↓
┌─────────────────────┐
│  本地服务 (Windows)  │
│  ┌───────────────┐  │
│  │ 接收请求       │  │
│  │ 执行爬虫代码   │  │
│  │ 保存到 MinIO   │  │
│  └───────────────┘  │
└─────────────────────┘
```

---

## ✅ 优势

- ✅ **完全分离**：Airflow 只负责调度，本地负责执行
- ✅ **资源隔离**：不影响 Airflow 容器
- ✅ **易于调试**：可以直接在本地运行
- ✅ **使用本地环境**：Chrome、配置都在本地

---

## 🔧 如果遇到问题

### 问题：Airflow 无法连接本地服务

**解决：**
1. 检查服务是否运行：访问 http://localhost:8000/health
2. 检查防火墙：允许 Python 通过防火墙
3. 修改 docker-compose.yml 添加 `extra_hosts`

### 问题：缺少依赖

**解决：**
```bash
pip install fastapi uvicorn
```

详细故障排除见：`WorkFlow/LOCAL_SERVICE_SETUP.md`

---

## 📚 更多信息

- 详细方案对比：`WorkFlow/LOCAL_EXECUTION_GUIDE.md`
- 设置指南：`WorkFlow/LOCAL_SERVICE_SETUP.md`
- 架构说明：`WorkFlow/SCHEDULING_VS_EXECUTION.md`

---

## 🎉 完成！

现在你的架构是：
- **Airflow**：负责调度和编排（轻量）
- **本地服务**：负责执行爬虫（资源密集型）

完美实现了分离！🎯


