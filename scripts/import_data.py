"""
数据导入脚本
将书籍内容通过 Qwen Embedding 处理后存入 Milvus (Zilliz Cloud)
"""

import json
import sys
from pathlib import Path
from typing import Generator

import httpx
from pymilvus import MilvusClient, DataType
from tqdm import tqdm

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import get_settings


def load_book_data(json_path: str) -> list[dict]:
    """加载书籍 JSON 数据"""
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def preprocess_data(raw_data: list[dict], book_name: str) -> list[dict]:
    """
    预处理数据：合并同一页的内容，过滤空内容

    返回格式: [{"page": "页码", "content": "合并后的内容", "book": "书名"}, ...]
    """
    # 按页码分组
    pages: dict[str, list[str]] = {}

    for item in raw_data:
        page = item.get("文件页码", "")
        content = item.get("内容", "").strip()

        if not page or not content:
            continue

        if page not in pages:
            pages[page] = []
        pages[page].append(content)

    # 合并同一页的内容
    processed = []
    for page, contents in pages.items():
        merged_content = "\n".join(contents)
        if len(merged_content) > 10:  # 过滤太短的内容
            processed.append(
                {"page": page, "content": merged_content, "book": book_name}
            )

    return processed


def get_embeddings_batch(
    texts: list[str], api_key: str, model: str = "text-embedding-v4"
) -> list[list[float]]:
    """
    批量获取文本的 embedding
    使用阿里云 DashScope API
    """
    url = "https://dashscope.aliyuncs.com/compatible-mode/v1/embeddings"

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    data = {"model": model, "input": texts, "encoding_format": "float"}

    with httpx.Client(timeout=60.0) as client:
        response = client.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()

    # 按 index 排序确保顺序正确
    embeddings_data = sorted(result["data"], key=lambda x: x["index"])
    return [item["embedding"] for item in embeddings_data]


def batch_generator(data: list, batch_size: int) -> Generator[list, None, None]:
    """将数据分批生成"""
    for i in range(0, len(data), batch_size):
        yield data[i : i + batch_size]


def create_collection(client: MilvusClient, collection_name: str, dimension: int):
    """创建 Milvus 集合"""
    # 检查集合是否存在
    if client.has_collection(collection_name):
        print(f"集合 {collection_name} 已存在，将删除并重新创建")
        client.drop_collection(collection_name)

    # 创建集合 schema
    schema = client.create_schema(auto_id=True, enable_dynamic_field=True)

    schema.add_field(
        field_name="id", datatype=DataType.INT64, is_primary=True, auto_id=True
    )
    schema.add_field(
        field_name="embedding", datatype=DataType.FLOAT_VECTOR, dim=dimension
    )
    schema.add_field(field_name="content", datatype=DataType.VARCHAR, max_length=65535)
    schema.add_field(field_name="page", datatype=DataType.VARCHAR, max_length=50)
    schema.add_field(field_name="book", datatype=DataType.VARCHAR, max_length=255)

    # 创建索引参数
    index_params = client.prepare_index_params()
    index_params.add_index(
        field_name="embedding", index_type="AUTOINDEX", metric_type="COSINE"
    )

    # 创建集合
    client.create_collection(
        collection_name=collection_name, schema=schema, index_params=index_params
    )

    print(f"集合 {collection_name} 创建成功")


def import_data_to_milvus(
    data: list[dict],
    client: MilvusClient,
    collection_name: str,
    api_key: str,
    embedding_model: str,
    batch_size: int = 20,
):
    """将数据导入到 Milvus"""
    total_batches = (len(data) + batch_size - 1) // batch_size

    for batch in tqdm(
        batch_generator(data, batch_size), total=total_batches, desc="导入数据"
    ):
        # 提取文本内容
        texts = [item["content"] for item in batch]

        # 获取 embeddings
        embeddings = get_embeddings_batch(texts, api_key, embedding_model)

        # 准备插入数据
        insert_data = []
        for item, embedding in zip(batch, embeddings):
            insert_data.append(
                {
                    "embedding": embedding,
                    "content": item["content"],
                    "page": item["page"],
                    "book": item["book"],
                }
            )

        # 插入数据
        client.insert(collection_name=collection_name, data=insert_data)

    print(f"成功导入 {len(data)} 条数据")


def main():
    """主函数"""
    settings = get_settings()

    # 验证配置
    if not settings.dashscope_api_key:
        print("错误: 请设置 DASHSCOPE_API_KEY 环境变量")
        sys.exit(1)

    if not settings.zilliz_cloud_uri or not settings.zilliz_cloud_token:
        print("错误: 请设置 ZILLIZ_CLOUD_URI 和 ZILLIZ_CLOUD_TOKEN 环境变量")
        sys.exit(1)

    # 数据文件路径
    project_root = Path(__file__).parent.parent
    json_file = project_root / f"{settings.book_name}.json"

    if not json_file.exists():
        print(f"错误: 找不到数据文件 {json_file}")
        sys.exit(1)

    print(f"正在加载数据文件: {json_file}")

    # 加载和预处理数据
    raw_data = load_book_data(str(json_file))
    print(f"原始数据条数: {len(raw_data)}")

    processed_data = preprocess_data(raw_data, settings.book_name)
    print(f"预处理后数据条数: {len(processed_data)}")

    # 连接 Milvus
    print(f"正在连接 Zilliz Cloud: {settings.zilliz_cloud_uri}")
    client = MilvusClient(
        uri=settings.zilliz_cloud_uri, token=settings.zilliz_cloud_token
    )

    # 创建集合
    create_collection(
        client, settings.milvus_collection_name, settings.embedding_dimension
    )

    # 导入数据
    import_data_to_milvus(
        processed_data,
        client,
        settings.milvus_collection_name,
        settings.dashscope_api_key,
        settings.embedding_model,
        batch_size=10,
    )

    print("数据导入完成!")


if __name__ == "__main__":
    main()
