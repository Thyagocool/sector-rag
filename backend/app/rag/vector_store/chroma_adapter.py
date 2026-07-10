"""Adapter do ChromaDB — implementa VectorStoreAdapter com suporte a setores."""

from langchain_chroma import Chroma
from app.config import settings
from app.rag.embeddings import get_embeddings
from app.rag.vector_store.protocol import VectorStoreAdapter
from langchain_core.documents import Document
import chromadb
from chromadb.config import Settings as ChromaSettings
import os

# Desliga telemetria do ChromaDB
_chroma_settings = ChromaSettings(
    anonymized_telemetry=False,
)


class ChromaAdapter(VectorStoreAdapter):
    """Banco vetorial usando ChromaDB com suporte a metadado de setor."""

    def __init__(self):
        persist_dir = settings.chroma_persist_dir
        os.makedirs(persist_dir, exist_ok=True)

        self._client = chromadb.PersistentClient(
            path=persist_dir,
            settings=_chroma_settings,
        )
        self._store = Chroma(
            collection_name=settings.collection_name,
            embedding_function=get_embeddings(),
            persist_directory=persist_dir,
            client=self._client,
        )

    def as_retriever(self, **kwargs):
        return self._store.as_retriever(**kwargs)

    def add_documents(self, docs: list[Document]):
        self._store.add_documents(docs)

    def clear_all(self):
        ids = self._store.get()["ids"]
        if ids:
            self._store.delete(ids)

    def list_collections(self) -> list[str]:
        return [str(c) for c in self._client.list_collections()]

    def list_sectors(self) -> list[str]:
        """Retorna setores unicos presentes nos metadados dos documentos."""
        all_data = self._store.get()
        sectors = set()
        for meta in all_data.get("metadatas", []):
            if meta and "sector" in meta:
                sectors.add(meta["sector"])
        return sorted(sectors)

    def get_chunks_by_sector(self, sector: str) -> list[dict]:
        """Retorna todos os chunks de um setor especifico."""
        results = self._store.get(where={"sector": sector})
        chunks = []
        for i in range(len(results["ids"])):
            chunks.append({
                "id": results["ids"][i],
                "content": results["documents"][i],
                "metadata": results["metadatas"][i] if results["metadatas"] else {},
            })
        return chunks

    def delete_by_sector(self, sector: str):
        """Remove todos os chunks de um setor."""
        results = self._store.get(where={"sector": sector})
        ids = results["ids"]
        if ids:
            self._store.delete(ids)

    def get_files_by_sector(self, sector: str) -> list[dict]:
        """Retorna arquivos unicos de um setor com seus chunks."""
        results = self._store.get(where={"sector": sector})
        files: dict[str, list[dict]] = {}
        for i in range(len(results["ids"])):
            meta = results["metadatas"][i] if results["metadatas"] else {}
            source = meta.get("source", "desconhecido")
            if source not in files:
                files[source] = []
            files[source].append({
                "id": results["ids"][i],
                "content": results["documents"][i],
                "metadata": meta,
            })
        # Ordena arquivos por nome
        return [
            {"filename": name, "chunks": chunks}
            for name, chunks in sorted(files.items())
        ]

    def get_chunks_by_topic(self, sector: str, source: str, topic: str) -> list[dict]:
        """Retorna chunks de um setor + arquivo + tópico específico."""
        results = self._store.get(where={
            "$and": [
                {"sector": sector},
                {"source": source},
                {"topic": topic},
            ]
        })
        chunks = []
        for i in range(len(results["ids"])):
            chunks.append({
                "id": results["ids"][i],
                "content": results["documents"][i],
                "metadata": results["metadatas"][i] if results["metadatas"] else {},
            })
        return chunks
