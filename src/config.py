"""
config.py - Central configuration management
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """Application settings"""
    
    # API Keys
    openai_api_key: str
    
    # Models
    embedding_model: str = "text-embedding-3-small"
    llm_model: str = "gpt-3.5-turbo"
    temperature: float = 0.1
    
    # Retrieval
    top_k: int = 5
    chunk_size: int = 512
    chunk_overlap: int = 50
    
    # Search
    hybrid_alpha: float = 0.7  # Weight for dense vs sparse
    use_reranking: bool = True
    
    # Cache
    enable_cache: bool = True
    cache_similarity_threshold: float = 0.95
    cache_ttl: int = 3600
    redis_url: str = "redis://localhost:6379"
    
    # Vector DB
    qdrant_url: str = "http://localhost:6333"
    collection_name: str = "financial_docs"
    vector_dimension: int = 1536  # text-embedding-3-small
    
    # Performance
    batch_size: int = 32
    max_concurrent_requests: int = 10
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()

# Print config on import (for debugging)
if __name__ == "__main__":
    print("Current Configuration:")
    print(f"  LLM Model: {settings.llm_model}")
    print(f"  Embedding Model: {settings.embedding_model}")
    print(f"  Top K: {settings.top_k}")
    print(f"  Cache Enabled: {settings.enable_cache}")
    print(f"  Hybrid Alpha: {settings.hybrid_alpha}")