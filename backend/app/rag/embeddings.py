"""Configuração de embeddings usando Ollama (100% gratuito e local)."""

from langchain_ollama import OllamaEmbeddings
from app.config import settings


def get_ollama_embeddings() -> OllamaEmbeddings:
    """Retorna o modelo de embeddings rodando via Ollama.

    Roda local, sem depender de API paga. Precisa do Ollama instalado
    e do modelo baixado:
        $ ollama pull nomic-embed-text
    """
    return OllamaEmbeddings(
        model=settings.embedding_model,
        base_url=settings.ollama_base_url,
    )


# Singleton esperto — se o modelo mudar nas settings, recria.
_embeddings: OllamaEmbeddings | None = None


def get_embeddings() -> OllamaEmbeddings:
    global _embeddings
    if _embeddings is None:
        _embeddings = get_ollama_embeddings()
    return _embeddings
