"""Reranking de documentos — melhora a qualidade das respostas.

Uso:
    from app.rag.reranking.reranker import rerank
    docs_reranked = rerank(pergunta, docs_recuperados, top_k=4)
"""

from app.rag.reranking.reranker import rerank, get_reranker

__all__ = ["rerank", "get_reranker"]
