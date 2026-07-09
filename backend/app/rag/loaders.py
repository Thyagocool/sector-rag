"""Loaders de documentos para varios formatos.

Estende os loaders padrao do LangChain com suporte a mais formatos.
"""

from pathlib import Path
from langchain_core.documents import Document
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    Docx2txtLoader,
    BSHTMLLoader,
    CSVLoader,
    JSONLoader,
)


def _jq_schema_for_json() -> str:
    """Retorna schema jq que extrai todos os textos de um JSON generico.

    Tenta extrair qualquer campo 'text', 'content', 'descricao',
    ou simplesmente converte o JSON inteiro em string.
    """
    # Schema generico: extrai o JSON todo como string
    return "."


def get_loader_for_file(file_path: Path):
    """Retorna o loader adequado para a extensao do arquivo.

    Retorna None se o formato nao for suportado.
    """
    ext = file_path.suffix.lower()

    loaders = {
        ".pdf": lambda p: PyPDFLoader(str(p)),
        ".txt": lambda p: TextLoader(str(p), encoding="utf-8"),
        ".md": lambda p: TextLoader(str(p), encoding="utf-8"),
        ".docx": lambda p: Docx2txtLoader(str(p)),
        ".html": lambda p: BSHTMLLoader(str(p), open_encoding="utf-8"),
        ".htm": lambda p: BSHTMLLoader(str(p), open_encoding="utf-8"),
        ".csv": lambda p: CSVLoader(str(p), encoding="utf-8"),
        ".json": lambda p: JSONLoader(
            file_path=str(p),
            jq_schema=_jq_schema_for_json(),
            text_content=False,
        ),
        ".py": lambda p: TextLoader(str(p), encoding="utf-8"),
        ".js": lambda p: TextLoader(str(p), encoding="utf-8"),
        ".ts": lambda p: TextLoader(str(p), encoding="utf-8"),
        ".sql": lambda p: TextLoader(str(p), encoding="utf-8"),
        ".yaml": lambda p: TextLoader(str(p), encoding="utf-8"),
        ".yml": lambda p: TextLoader(str(p), encoding="utf-8"),
        ".xml": lambda p: TextLoader(str(p), encoding="utf-8"),
    }

    loader_fn = loaders.get(ext)
    if loader_fn is None:
        return None

    return loader_fn(file_path)


def load_document(file_path: Path) -> list[Document]:
    """Carrega um documento do disco.

    Args:
        file_path: Caminho do arquivo.

    Returns:
        Lista de Document carregados (ainda sem chunking).

    Raises:
        ValueError se o formato nao for suportado.
    """
    loader = get_loader_for_file(file_path)
    if loader is None:
        ext = file_path.suffix.lower()
        raise ValueError(f"Formato nao suportado: {ext}")
    return loader.load()


SUPPORTED_EXTENSIONS = {
    ".pdf", ".txt", ".md", ".docx",
    ".html", ".htm", ".csv", ".json",
    ".py", ".js", ".ts", ".sql",
    ".yaml", ".yml", ".xml",
}
