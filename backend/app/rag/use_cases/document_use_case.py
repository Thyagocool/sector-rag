"""Use case: gerenciar documentos (upload, ingestao, limpeza por setor)."""

from pathlib import Path
from langchain_core.documents import Document
from app.rag.vector_store import VectorStoreAdapter, get_vector_store_adapter
from app.rag.chunking import get_chunking_strategy, ChunkingStrategy
from app.rag.chunking.strategies import RecursiveChunking
from app.rag.loaders import load_document, SUPPORTED_EXTENSIONS
import logging

logger = logging.getLogger(__name__)


class DocumentUseCase:
    """Upload, chunking, ingestao e limpeza de documentos no banco vetorial."""

    SUPPORTED_EXTENSIONS = SUPPORTED_EXTENSIONS

    def __init__(
        self,
        vector_store: VectorStoreAdapter | None = None,
        chunking_strategy: ChunkingStrategy | None = None,
    ):
        self._vector_store = vector_store
        self._chunking_strategy = chunking_strategy or RecursiveChunking(
            chunk_size=1000, chunk_overlap=200
        )

    def _get_store(self) -> VectorStoreAdapter:
        if self._vector_store is None:
            self._vector_store = get_vector_store_adapter()
        return self._vector_store

    def load_and_chunk(self, file_path: Path, sector: str = "geral") -> list[Document]:
        """Carrega um documento do disco, aplica chunking e adiciona metadado de setor.

        1. Detecta o formato e carrega com o loader adequado
        2. Aplica a estrategia de chunking configurada
        3. Adiciona metadado 'sector' e 'source' em cada chunk
        """
        docs = load_document(file_path)
        logger.info(
            "%s carregado: %d documento(s) bruto(s)",
            file_path.name, len(docs),
        )

        chunks = self._chunking_strategy.split(docs)
        logger.info(
            "Chunking concluido: %d chunks gerados", len(chunks),
        )

        # Adiciona metadado de setor em cada chunk
        for chunk in chunks:
            chunk.metadata["sector"] = sector
            chunk.metadata["source"] = file_path.name

        return chunks

    def ingest_documents(self, docs: list[Document]):
        """Ingere documentos (chunks) no banco vetorial."""
        store = self._get_store()
        store.add_documents(docs)
        logger.info("%d chunk(s) ingerido(s)", len(docs))

    def clear_all(self):
        """Limpa todo o banco vetorial."""
        store = self._get_store()
        store.clear_all()
        logger.info("Banco vetorial limpo")
