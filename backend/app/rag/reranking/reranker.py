"""Reranking de documentos usando cross-encoder.

Melhora a qualidade das respostas re-ordenando os documentos
recuperados pelo similarity search.

Nota: requer sentence-transformers (com PyTorch). Se nao estiver
instalado, o reranking apenas retorna os documentos originais.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Modelo tiny de cross-encoder (~80MB, roda em CPU)
DEFAULT_MODEL = "cross-encoder/ms-marco-MiniLM-L-2-v2"

_reranker: Optional[object] = None


def _is_available() -> bool:
    """Verifica se sentence-transformers esta instalado."""
    try:
        import sentence_transformers  # noqa: F401
        return True
    except ImportError:
        return False


def get_reranker(model_name: str = DEFAULT_MODEL):
    """Retorna instancia do cross-encoder (cacheada).

    Retorna None se sentence-transformers nao estiver instalado.
    """
    global _reranker
    if not _is_available():
        logger.warning("sentence-transformers nao instalado — reranking desativado")
        return None

    if _reranker is None:
        try:
            from sentence_transformers import CrossEncoder
            logger.info("Carregando reranker: %s...", model_name)
            _reranker = CrossEncoder(model_name, max_length=512)
            logger.info("Reranker pronto")
        except Exception as exc:
            logger.warning("Falha ao carregar reranker: %s", exc)
            return None

    return _reranker


def rerank(
    query: str,
    documents: list,
    top_k: int = 4,
    model_name: str = DEFAULT_MODEL,
) -> list:
    """Re-ordena documentos por relevancia a pergunta.

    Se sentence-transformers nao estiver instalado, retorna
    os documentos originais sem reordenar.

    Args:
        query: Pergunta do usuario.
        documents: Lista de Document do LangChain.
        top_k: Quantos documentos retornar depois do rerank.
        model_name: Nome do modelo cross-encoder.

    Returns:
        Lista dos top_k documentos (re-ordenados se disponivel).
    """
    if not documents:
        return documents

    model = get_reranker(model_name)
    if model is None:
        logger.debug("Reranking indisponivel — retornando documentos originais")
        return documents[:top_k]

    from sentence_transformers import CrossEncoder
    assert isinstance(model, CrossEncoder)

    # Prepara pares (pergunta, conteudo) pro cross-encoder
    pairs = [(query, doc.page_content) for doc in documents]

    # Cross-encoder retorna scores de relevancia
    scores = model.predict(pairs)

    # Junta scores com documentos e ordena
    scored = list(zip(scores, documents))
    scored.sort(key=lambda x: x[0], reverse=True)

    # Retorna os top_k mais relevantes
    reranked = [doc for _, doc in scored[:top_k]]

    logger.debug(
        "Rerank: %d docs -> scores %s -> top %d",
        len(documents),
        [round(float(s), 3) for s in sorted(scores, reverse=True)],
        top_k,
    )

    return reranked
