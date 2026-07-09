# Dia 4 — Chunking esperto + mais formatos de documento

## O que foi feito

### Chunking inteligente (app/rag/chunking/)
Criado modulo com estrategias de chunking reutilizaveis:

| Estrategia | Arquivo | Como funciona |
|------------|---------|---------------|
| **RecursiveChunking** | `strategies.py` | Quebra por separadores (paragrafo, frase, palavra). Padrao para qualquer texto |
| **MarkdownChunking** | `strategies.py` | Quebra por cabecalhos Markdown (`#`, `##`, `###`). Ideal pra `.md` |
| **CodeChunking** | `strategies.py` | Quebra codigo respeitando funcoes e classes. Suporta Python, JS, TS, Java, Go, Ruby, Rust, C++, C#, PHP |
| **SemanticChunking** | `strategies.py` | Placeholder pra chunking por similaridade semantica (TODO) |

Cada estrategia implementa a interface:
```python
class ChunkingStrategy(ABC):
    @abstractmethod
    def split(self, documents: list[Document]) -> list[Document]:
        ...
```

Factory em `__init__.py` com lookup por nome:
```python
strategy = get_chunking_strategy("markdown", chunk_size=800, chunk_overlap=150)
```

### Novos formatos de documento (app/rag/loaders.py)

Criado modulo centralizado de loaders. Nova lista completa:

| Extensao | Loader | Biblioteca |
|----------|--------|-----------|
| `.pdf` | PyPDFLoader | pypdf |
| `.txt` | TextLoader | nativo |
| `.md` | TextLoader | nativo |
| `.docx` | Docx2txtLoader | python-docx |
| `.html` / `.htm` | BSHTMLLoader | beautifulsoup4 + lxml |
| `.csv` | CSVLoader | nativo |
| `.json` | JSONLoader | nativo |
| `.py` / `.js` / `.ts` | TextLoader | nativo |
| `.sql` / `.yaml` / `.yml` / `.xml` | TextLoader | nativo |

**Total: 15 extensoes suportadas.**

### DocumentUseCase atualizado

O fluxo de upload era:
```
upload -> load_document() -> ingest_documents()
```

Agora eh:
```
upload -> load_and_chunk() -> ingest_documents()
                              ^-- chunks prontos
         load_document() + chunking_strategy.split()
```

O `DocumentUseCase` agora recebe opcionalmente uma `ChunkingStrategy` via construtor (DI). Padrao: `RecursiveChunking(1000, 200)`.

## Estrutura de arquivos
```
app/rag/
├── chunking/
│   ├── __init__.py        ← factory
│   └── strategies.py      ← 4 estrategias
├── loaders.py             ← loaders para 15 formatos
├── use_cases/
│   └── document_use_case.py  ← agora com chunking
└── routes.py              ← aceita novos formatos
```

## Como testar
```bash
# Upload de HTML
curl -X POST http://localhost:8000/api/v1/upload \
  -F "file=@pagina.html"

# Upload de CSV
curl -X POST http://localhost:8000/api/v1/upload \
  -F "file=@dados.csv"

# Upload de Python
curl -X POST http://localhost:8000/api/v1/upload \
  -F "file=@script.py"
```

## Proximos passos
- Implementar `SemanticChunking` completo com sliding window + similaridade de cosseno
- Adicionar config pra escolher chunking strategy via query param
- Testar impactos em qualidade com diferentes chunk_sizes
