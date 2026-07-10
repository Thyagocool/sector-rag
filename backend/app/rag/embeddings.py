"""Configuração de embeddings usando Ollama (100% gratuito e local).

Usa um wrapper com batch para enviar textos em lotes ao Ollama,
evitando timeouts com muitos chunks.
"""

import logging
from langchain_ollama import OllamaEmbeddings
from app.config import settings

logger = logging.getLogger(__name__)

_EMBED_BATCH_SIZE = 50  # envia no maximo 50 textos por request ao Ollama


class BatchedOllamaEmbeddings:
    """Wrapper que divide embed_documents em lotes menores.

    O OllamaEmbeddings original manda tudo num request so, o que
    pode travar ou estourar timeout com muitos chunks. Essa wrapper
    quebra em lotes de _EMBED_BATCH_SIZE.
    """

    def __init__(self, embeddings: OllamaEmbeddings, batch_size: int = _EMBED_BATCH_SIZE):
        self._embeddings = embeddings
        self._batch_size = batch_size

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Gera embeddings em lotes, impedindo requests monstruosos."""
        if len(texts) <= self._batch_size:
            return self._embeddings.embed_documents(texts)

        logger.info(
            "Embeddings em lote: %d textos em lotes de %d",
            len(texts), self._batch_size,
        )
        all_embeddings: list[list[float]] = []
        for i in range(0, len(texts), self._batch_size):
            batch = texts[i:i + self._batch_size]
            batch_emb = self._embeddings.embed_documents(batch)
            all_embeddings.extend(batch_emb)
            logger.debug("Lote %d/%d concluido", i // self._batch_size + 1, (len(texts) - 1) // self._batch_size + 1)
        return all_embeddings

    def embed_query(self, text: str) -> list[float]:
        """Embeddings de query (unico texto, sem batch)."""
        return self._embeddings.embed_query(text)


def get_ollama_embeddings() -> BatchedOllamaEmbeddings:
    """Retorna embeddings Ollama com batch (evita travamentos)."""
    raw = OllamaEmbeddings(
        model=settings.embedding_model,
        base_url=settings.ollama_base_url,
        client_kwargs={"timeout": 300},  # 5 min timeout pra cada lote
    )
    return BatchedOllamaEmbeddings(raw)


# Singleton
_embeddings: BatchedOllamaEmbeddings | None = None


def get_embeddings() -> BatchedOllamaEmbeddings:
    global _embeddings
    if _embeddings is None:
        _embeddings = get_ollama_embeddings()
    return _embeddings
