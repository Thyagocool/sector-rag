"""Estrategias de chunking (divisao inteligente de documentos)."""

from abc import ABC, abstractmethod
from langchain_core.documents import Document
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    MarkdownHeaderTextSplitter,
    PythonCodeTextSplitter,
    Language,
)


class ChunkingStrategy(ABC):
    """Interface para qualquer estrategia de chunking."""

    @abstractmethod
    def split(self, documents: list[Document]) -> list[Document]:
        """Recebe documentos inteiros, retorna chunks."""
        ...


class RecursiveChunking(ChunkingStrategy):
    """Quebra o texto recursivamente por separadores.

    Funciona pra qualquer formato. É o padrao mais seguro.
    """

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap

    def split(self, documents: list[Document]) -> list[Document]:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self._chunk_size,
            chunk_overlap=self._chunk_overlap,
            separators=["\n\n", "\n", ".", " ", ""],
        )
        return splitter.split_documents(documents)


class MarkdownChunking(ChunkingStrategy):
    """Quebra documentos Markdown pelos cabecalhos (##, ###, etc).

    Ideal para arquivos .md — respeita a estrutura logica.
    """

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap

    def split(self, documents: list[Document]) -> list[Document]:
        headers_to_split_on = [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
        ]
        splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=headers_to_split_on,
        )

        # MarkdownHeaderTextSplitter so aceita string, entao processamos
        # doc por doc e mantemos metadados originais
        result = []
        for doc in documents:
            chunks = splitter.split_text(doc.page_content)
            for chunk in chunks:
                chunk.metadata.update(doc.metadata)
            result.extend(chunks)

        # Po s split por tamanho nos chunks resultantes
        # (se um cabecalho foi muito grande)
        size_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self._chunk_size,
            chunk_overlap=self._chunk_overlap,
        )
        return size_splitter.split_documents(result)


class CodeChunking(ChunkingStrategy):
    """Quebra codigo fonte respeitando funcoes e classes.

    Suporta: Python, JS, Java, Go, Ruby, Rust, SQL, etc.
    """

    LANG_MAP = {
        ".py": Language.PYTHON,
        ".js": Language.JS,
        ".ts": Language.TS,
        ".java": Language.JAVA,
        ".go": Language.GO,
        ".rb": Language.RUBY,
        ".rs": Language.RUST,
        ".cpp": Language.CPP,
        ".cs": Language.CSHARP,
        ".php": Language.PHP,
    }

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap

    def split(self, documents: list[Document]) -> list[Document]:
        result = []
        for doc in documents:
            ext = doc.metadata.get("source", "")
            if isinstance(ext, str):
                # tenta pegar extensao do path
                import os
                ext = os.path.splitext(ext)[1].lower()
            lang = self.LANG_MAP.get(ext, Language.PYTHON)  # fallback python

            splitter = RecursiveCharacterTextSplitter.from_language(
                language=lang,
                chunk_size=self._chunk_size,
                chunk_overlap=self._chunk_overlap,
            )
            chunks = splitter.split_documents([doc])
            result.extend(chunks)

        return result


class SemanticChunking(ChunkingStrategy):
    """Chunking semantico — agrupa frases por similaridade.

    Usa embeddings pra detectar "pausas naturais" no texto,
    quebrando onde o assunto muda.
    """

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        min_chunk_size: int = 50,
    ):
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap
        self._min_chunk_size = min_chunk_size

    def split(self, documents: list[Document]) -> list[Document]:
        """Por enquanto, usa RecursiveChunking como fallback.

        A implementacao completa com embeddings de similaridade
        exige um modelo de embedding extra. Para nao travar o setup,
        comecamos com o recursive e evoluimos depois.
        """
        # TODO: implementar chunking semantico de verdade
        # com sliding window + similaridade de cosseno entre janelas
        fallback = RecursiveChunking(
            chunk_size=self._chunk_size,
            chunk_overlap=self._chunk_overlap,
        )
        return fallback.split(documents)
