"""Fabrica de adaptadores do banco vetorial.

Aqui eh o unico lugar que precisa mudar quando trocar de banco.
Exemplo futuro:
    if settings.vector_store == "pgvector":
        from .pgvector_adapter import PGVectorAdapter
        return PGVectorAdapter()
"""

from app.rag.vector_store.protocol import VectorStoreAdapter
from app.rag.vector_store.chroma_adapter import ChromaAdapter

_vector_store: VectorStoreAdapter | None = None


def get_vector_store_adapter() -> VectorStoreAdapter:
    """Retorna o adapter do banco vetorial (cacheado).

    Para migrar de banco, troque o ChromaAdapter pela implementacao nova.
    """
    global _vector_store
    if _vector_store is None:
        _vector_store = ChromaAdapter()
    return _vector_store
