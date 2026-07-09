from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # --- Ollama ---
    ollama_base_url: str = "http://localhost:11434"
    llm_model: str = "qwen2.5:0.5b"
    embedding_model: str = "nomic-embed-text"

    # --- ChromaDB ---
    chroma_persist_dir: str = "./data/chroma"
    collection_name: str = "rag_docs"

    # --- App ---
    app_name: str = "Sector-RAG"
    app_version: str = "1.0.0"
    debug: bool = True
    cors_origins: list[str] = ["*"]

    # --- Reranking ---
    rag_reranking_enabled: bool = False
    rag_reranking_top_k: int = 4

    # --- Upload ---
    max_upload_size_mb: int = 50

    model_config = {"env_prefix": "RAG_", "env_file": ".env"}


settings = Settings()
