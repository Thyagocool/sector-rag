"""Use case: gerenciar documentos (upload, ingestao, limpeza por setor)."""

import re
from pathlib import Path
from langchain_core.documents import Document
from app.rag.vector_store import VectorStoreAdapter, get_vector_store_adapter
from app.rag.chunking import get_chunking_strategy, ChunkingStrategy
from app.rag.chunking.strategies import RecursiveChunking
from app.rag.loaders import load_document, SUPPORTED_EXTENSIONS
import logging

logger = logging.getLogger(__name__)


def _extract_topic(text: str, max_chars: int = 70) -> str:
    """Extrai um topic curto do inicio do texto."""
    # Pega a primeira linha nao-vazia
    for line in text.split("\n"):
        line = line.strip()
        if line and len(line) > 3:
            # Remove numeros de pagina e marcacoes
            clean = re.sub(r"^\d+\s*", "", line).strip()
            if clean:
                return clean[:max_chars].rstrip(".,;: ")
    # Fallback: primeiros chars
    return text[:max_chars].rstrip(".,;: ") + "..."


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
            chunk_size=10000, chunk_overlap=1000
        )

    def _get_store(self) -> VectorStoreAdapter:
        if self._vector_store is None:
            self._vector_store = get_vector_store_adapter()
        return self._vector_store

    def load_and_chunk(self, file_path: Path, sector: str = "geral", source_name: str | None = None) -> list[Document]:
        """Carrega um documento e aplica chunking hierárquico (2 níveis).

        Nível 1 (seção): chunk_size=10000 → cada chunk vira um "tópico"
        Nível 2 (subseção): cada seção é refatiada em chunk_size=2000 → "subtópicos"

        Metadados:
          - sector, source, topic (título da seção), subtopic (título da subseção)
        """
        docs = load_document(file_path)
        logger.info("%s carregado: %d documento(s) bruto(s)", file_path.name, len(docs))

        # ── Nível 1: fatia em seções grandes ──────────────────────────
        section_splitters = RecursiveChunking(chunk_size=10000, chunk_overlap=1000)
        sections = section_splitters.split(docs)
        logger.info("Nível 1 (seções): %d seções geradas", len(sections))

        # ── Nível 2: cada seção em subseções ──────────────────────────
        sub_splitters = RecursiveChunking(chunk_size=2000, chunk_overlap=300)
        source = source_name or file_path.name
        all_chunks: list[Document] = []

        for idx, section in enumerate(sections):
            topic = _extract_topic(section.page_content)
            subchunks = sub_splitters.split([section])
            for sub in subchunks:
                sub.metadata["sector"] = sector
                sub.metadata["source"] = source
                sub.metadata["topic"] = topic
                sub.metadata["subtopic"] = _extract_topic(sub.page_content)
                sub.metadata["level"] = 2
                all_chunks.append(sub)

        logger.info(
            "Chunking hierárquico concluído: %d subseções em %d seções",
            len(all_chunks), len(sections),
        )
        return all_chunks

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
