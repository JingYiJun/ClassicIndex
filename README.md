# 📚 Classic Index - 经典著作语义搜索

[![Docker Build](https://github.com/jingyijun/ClassicIndex/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/jingyijun/ClassicIndex/actions/workflows/docker-publish.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

基于 Qwen Embedding 和 Milvus (Zilliz Cloud) 构建的语义搜索应用，帮助你在经典著作中快速找到最匹配的段落和页码。

## ✨ 功能特点

- **语义搜索**: 使用 Qwen Embedding 进行语义理解，不仅仅是关键词匹配
- **快速检索**: 基于 Milvus 向量数据库的高效相似度搜索
- **精确定位**: 返回匹配段落对应的页码，便于查阅原文
- **美观界面**: Streamlit 构建的现代化 UI
- **容器化部署**: 支持 Docker Compose 一键部署

## 🏗️ 技术架构

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Streamlit     │────▶│    FastAPI      │────▶│  Zilliz Cloud   │
│   Frontend      │◀────│    Backend      │◀────│    (Milvus)     │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │  DashScope API  │
                        │ (Qwen Embedding)│
                        └─────────────────┘
```

## 🐳 Docker Compose 部署（推荐）

这是最简单的部署方式，前后端已打包在同一个镜像中。

### 1. 准备环境变量

创建 `.env` 文件：

```bash
# Qwen API 配置 (通过阿里云 DashScope)
DASHSCOPE_API_KEY=your_dashscope_api_key_here

# Zilliz Cloud (Milvus) 配置
ZILLIZ_CLOUD_URI=https://your-instance.zillizcloud.com
ZILLIZ_CLOUD_TOKEN=your_zilliz_cloud_token_here

# 可选配置
MILVUS_COLLECTION_NAME=classic_books
BOOK_NAME=马克思全集1
```

### 2. 使用预构建镜像部署

```bash
# 下载 docker-compose.yml
curl -O https://raw.githubusercontent.com/jingyijun/ClassicIndex/main/docker-compose.yml

# 启动服务
docker compose up -d
```

### 3. 或者从源码构建

```bash
# 克隆仓库
git clone https://github.com/jingyijun/ClassicIndex.git
cd ClassicIndex

# 构建并启动
docker compose up -d --build
```

### 4. 访问服务

- **前端界面**: http://localhost:8501
- **后端 API**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs

### 5. 查看日志

```bash
# 查看所有日志
docker compose logs -f

# 仅查看应用日志
docker compose logs -f classic-index
```

### 6. 停止服务

```bash
docker compose down
```

## 🔑 获取 API 密钥

在部署前，你需要获取以下 API 密钥：

| 服务         | 用途               | 获取地址                                                  |
| ------------ | ------------------ | --------------------------------------------------------- |
| DashScope    | Qwen Embedding API | [阿里云 DashScope](https://dashscope.console.aliyun.com/) |
| Zilliz Cloud | 向量数据库托管     | [Zilliz Cloud](https://cloud.zilliz.com/) (有免费额度)    |

### DashScope API 配置步骤

1. 访问 [阿里云 DashScope](https://dashscope.console.aliyun.com/)
2. 注册/登录后创建 API Key
3. 将 API Key 填入环境变量 `DASHSCOPE_API_KEY`

### Zilliz Cloud 配置步骤

1. 访问 [Zilliz Cloud](https://cloud.zilliz.com/)
2. 创建免费集群 (Free Tier)
3. 在集群详情页获取：
   - **Public Endpoint** → 填入 `ZILLIZ_CLOUD_URI`
   - **API Key** → 填入 `ZILLIZ_CLOUD_TOKEN`

## 📥 导入数据

在使用搜索功能前，需要先将书籍数据导入到 Milvus。

### 使用 Docker 导入

```bash
# 进入容器
docker compose exec classic-index bash

# 将数据文件放入 /app 目录后运行
python scripts/import_data.py
```

### 本地导入

```bash
# 确保已配置 .env 文件
python scripts/import_data.py
```

## 🚀 本地开发

如果你需要本地开发，可以按以下步骤操作：

### 1. 安装依赖

```bash
# 使用 uv (推荐)
uv sync

# 或使用 pip
pip install -e .
```

### 2. 配置环境变量

```bash
cp env.example .env
# 编辑 .env 文件填入 API 密钥
```

### 3. 导入数据

```bash
python scripts/import_data.py
```

### 4. 启动服务

```bash
# 启动后端 (终端 1)
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# 启动前端 (终端 2)
streamlit run frontend/app.py
```

访问 http://localhost:8501 开始使用！

## 📁 项目结构

```
ClassicIndex/
├── .github/
│   └── workflows/
│       └── docker-publish.yml  # GitHub Actions 构建配置
├── backend/
│   ├── __init__.py
│   └── main.py                 # FastAPI 后端服务
├── frontend/
│   ├── __init__.py
│   └── app.py                  # Streamlit 前端应用
├── scripts/
│   ├── __init__.py
│   └── import_data.py          # 数据导入脚本
├── config.py                   # 配置管理
├── main.py                     # 主入口文件
├── pyproject.toml              # 项目依赖
├── Dockerfile                  # Docker 构建文件
├── docker-compose.yml          # Docker Compose 配置
├── env.example                 # 环境变量模板
├── LICENSE                     # MIT 许可证
└── README.md                   # 项目文档
```

## 📖 数据格式

书籍 JSON 文件格式：

```json
[
  {
    "文件页码": "1",
    "内容": "这是页面内容...",
    "逻辑页码": ""
  },
  ...
]
```

## 🔧 API 接口

### 搜索接口

```http
POST /search
Content-Type: application/json

{
  "query": "你的搜索内容",
  "top_k": 10
}
```

响应：

```json
{
  "results": [
    {
      "content": "匹配的文本内容",
      "page": "42",
      "book": "马克思全集1",
      "score": 0.89
    }
  ],
  "query": "你的搜索内容"
}
```

### 健康检查

```http
GET /health
```

### API 文档

启动服务后访问 http://localhost:8000/docs 查看完整的 Swagger API 文档。

## 🔄 CI/CD

本项目使用 GitHub Actions 自动构建 Docker 镜像并推送到 GitHub Container Registry (ghcr.io)。

### 触发条件

- 推送到 `main` 或 `master` 分支
- 创建版本标签 (如 `v1.0.0`)
- Pull Request (仅构建不推送)

### 镜像标签

| 触发事件        | 标签示例                |
| --------------- | ----------------------- |
| main 分支推送   | `latest`, `sha-abc1234` |
| 版本标签 v1.2.3 | `1.2.3`, `1.2`, `1`     |

### 手动拉取镜像

```bash
docker pull ghcr.io/jingyijun/classicindex:latest
```

## 🛠️ 故障排除

### 常见问题

**Q: 无法连接到后端服务？**

A: 确保后端服务正在运行，检查端口 8000 是否被占用。

**Q: Embedding API 调用失败？**

A: 检查 `DASHSCOPE_API_KEY` 是否正确设置，确认 API 配额是否充足。

**Q: Milvus 连接失败？**

A: 确认 `ZILLIZ_CLOUD_URI` 和 `ZILLIZ_CLOUD_TOKEN` 配置正确。

**Q: Docker 容器启动失败？**

A: 查看日志 `docker compose logs -f`，确认环境变量是否正确配置。

## 📝 License

[MIT License](LICENSE)
