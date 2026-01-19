"""配置文件 - 管理所有环境变量和配置"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置"""

    # DashScope (Qwen) API 配置
    dashscope_api_key: str = ""

    # Zilliz Cloud 配置
    zilliz_cloud_uri: str = ""
    zilliz_cloud_token: str = ""

    # Milvus 集合配置
    milvus_collection_name: str = "classic_books"

    # Embedding 配置
    embedding_model: str = "text-embedding-v4"  # Qwen 的 embedding 模型
    embedding_dimension: int = 1024  # text-embedding-v4 的维度

    # 书籍配置
    book_name: str = "马克思全集1"

    # API 配置
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()
