"""
FastAPI 后端服务
提供语义搜索 API
"""

import sys
from pathlib import Path
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymilvus import MilvusClient

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import get_settings

# 全局变量
milvus_client: MilvusClient | None = None
settings = get_settings()


class SearchRequest(BaseModel):
    """搜索请求模型"""

    query: str
    top_k: int = 10
    book_filter: str | None = None  # 可选的书籍过滤


class SearchResult(BaseModel):
    """单条搜索结果"""

    content: str
    page: str
    book: str
    score: float


class SearchResponse(BaseModel):
    """搜索响应模型"""

    results: list[SearchResult]
    query: str


async def get_embedding(text: str) -> list[float]:
    """
    获取文本的 embedding
    使用阿里云 DashScope API
    """
    url = "https://dashscope.aliyuncs.com/compatible-mode/v1/embeddings"

    headers = {
        "Authorization": f"Bearer {settings.dashscope_api_key}",
        "Content-Type": "application/json",
    }

    data = {
        "model": settings.embedding_model,
        "input": [text],
        "encoding_format": "float",
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()

    return result["data"][0]["embedding"]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global milvus_client

    # 启动时连接 Milvus
    print(f"正在连接 Zilliz Cloud: {settings.zilliz_cloud_uri}")
    milvus_client = MilvusClient(
        uri=settings.zilliz_cloud_uri, token=settings.zilliz_cloud_token
    )
    print("Milvus 连接成功")

    yield

    # 关闭时断开连接
    if milvus_client:
        milvus_client.close()
        print("Milvus 连接已关闭")


# 创建 FastAPI 应用
app = FastAPI(
    title="Classic Index API",
    description="经典著作语义搜索 API",
    version="1.0.0",
    lifespan=lifespan,
)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy"}


@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """
    语义搜索接口

    根据用户输入查找最匹配的文本段落
    """
    if not milvus_client:
        raise HTTPException(status_code=503, detail="Milvus 服务未连接")

    if not request.query.strip():
        raise HTTPException(status_code=400, detail="查询内容不能为空")

    try:
        # 获取查询文本的 embedding
        query_embedding = await get_embedding(request.query)

        # 构建过滤条件
        filter_expr = ""
        if request.book_filter:
            filter_expr = f'book == "{request.book_filter}"'

        # 在 Milvus 中搜索
        search_params = {"metric_type": "COSINE", "params": {"nprobe": 10}}

        results = milvus_client.search(
            collection_name=settings.milvus_collection_name,
            data=[query_embedding],
            limit=request.top_k,
            output_fields=["content", "page", "book"],
            filter=filter_expr if filter_expr else None,
            search_params=search_params,
        )

        # 格式化结果
        search_results = []
        for hits in results:
            for hit in hits:
                search_results.append(
                    SearchResult(
                        content=hit["entity"]["content"],
                        page=hit["entity"]["page"],
                        book=hit["entity"]["book"],
                        score=hit["distance"],  # COSINE 相似度
                    )
                )

        return SearchResponse(results=search_results, query=request.query)

    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Embedding API 调用失败: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@app.get("/collections")
async def list_collections():
    """列出所有集合"""
    if not milvus_client:
        raise HTTPException(status_code=503, detail="Milvus 服务未连接")

    collections = milvus_client.list_collections()
    return {"collections": collections}


@app.get("/collection/{collection_name}/stats")
async def collection_stats(collection_name: str):
    """获取集合统计信息"""
    if not milvus_client:
        raise HTTPException(status_code=503, detail="Milvus 服务未连接")

    try:
        stats = milvus_client.get_collection_stats(collection_name)
        return stats
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"集合不存在或获取失败: {str(e)}")


def start_server():
    """启动服务器"""
    import uvicorn

    uvicorn.run(
        "backend.main:app", host=settings.api_host, port=settings.api_port, reload=True
    )


if __name__ == "__main__":
    start_server()
