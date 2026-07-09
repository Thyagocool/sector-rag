"""Fabrica de estrategias de chunking.

Uso:
    strategy = get_chunking_strategy("recursive", chunk_size=800)
    chunks = strategy.split(documents)
"""

from app.rag.chunking.strategies import (
    ChunkingStrategy,
    RecursiveChunking,
    MarkdownChunking,
    CodeChunking,
    SemanticChunking,
)


def get_chunking_strategy(
    name: str = "recursive",
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> ChunkingStrategy:
    """Retorna a estrategia de chunking pelo nome.

    Nomes disponiveis: recursive, markdown, code, semantic.
    """
    strategy_map = {
        "recursive": RecursiveChunking,
        "markdown": MarkdownChunking,
        "code": CodeChunking,
        "semantic": SemanticChunking,
    }
    cls = strategy_map.get(name.lower())
    if cls is None:
        available = ", ".join(strategy_map.keys())
        raise ValueError(
            f"Estrategia desconhecida: '{name}'. Disponiveis: {available}"
        )
    return cls(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
