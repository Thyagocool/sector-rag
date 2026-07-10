"""Protocolo abstrato para o banco vetorial.

Permite trocar de implementacao (ChromaDB, pgvector, Pinecone...)
sem modificar o codigo dos use cases — so criar um novo adapter.
"""

from abc import ABC, abstractmethod
from langchain_core.documents import Document


class VectorStoreAdapter(ABC):
    """Interface que qualquer banco vetorial precisa implementar."""

    @abstractmethod
    def as_retriever(self, **kwargs):
        """Retorna um retriever configurado para buscas de similaridade."""
        ...

    @abstractmethod
    def add_documents(self, docs: list[Document]):
        """Adiciona documentos ao banco vetorial."""
        ...

    @abstractmethod
    def clear_all(self):
        """Remove todos os documentos do banco."""
        ...

    @abstractmethod
    def list_collections(self) -> list[str]:
        """Lista as colecoes/disponiveis."""
        ...

    @abstractmethod
    def list_sectors(self) -> list[str]:
        """Lista setores unicos presentes nos metadados."""
        ...

    @abstractmethod
    def get_chunks_by_sector(self, sector: str) -> list[dict]:
        """Retorna todos os chunks de um setor."""
        ...

    @abstractmethod
    def delete_by_sector(self, sector: str):
        """Remove todos os chunks de um setor."""
        ...

    @abstractmethod
    def get_files_by_sector(self, sector: str) -> list[dict]:
        """Retorna arquivos unicos de um setor com seus chunks.
        
        Cada item: {"filename": str, "chunks": list[dict]}
        """
        ...

    @abstractmethod
    def get_chunks_by_topic(self, sector: str, source: str, topic: str) -> list[dict]:
        """Retorna chunks de um setor + arquivo + tópico específico.
        
        Cada item: {"id": str, "content": str, "metadata": dict}
        """
        ...
