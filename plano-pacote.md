# 🎯 Plano de Empacotamento — Sector-RAG em um Único Executável

## Contexto Geral

Projeto **Sector-RAG**: app estilo WhatsApp para chat com documentos.
- **Upload de arquivos** (PDF, DOCX, TXT)
- **Chunking hierárquico** (seção + subseção) com armazenamento no ChromaDB
- **Navegação em árvore de 3 níveis**: Arquivo → Tópico → Subtópico (conteúdo inline)
- **Chat scoped** por setor / arquivo / tópico
- **Ollama** servindo modelo local (`nomic-embed-text` pra embedding, LLM pra resposta)

Já implementado:
- ✅ Chunking hierárquico (2 passos: 10000 → 2000 chars)
- ✅ Árvore de 3 níveis no frontend (File → Topic → Subtopic)
- ✅ Subtópico expansível com conteúdo inline
- ✅ Filtro por `topic` e `subtopic` no /ask
- ✅ Componentes Toast, Spinner, etc

---

## 🥇 Caminho Escolhido: `llama-cpp-python` + PyInstaller

### Por quê?
- Substitui o **processo externo do Ollama** por uma lib Python nativa
- Permite PyInstaller empacotar **tudo num `.exe`/binário único**
- Modelos .gguf vão como *data files* ou baixados na primeira execução

### Tamanhos estimados

| Componente | Tamanho |
|---|---|
| Executável (Python + libs + ChromaDB + llama-cpp-python + frontend) | ~120 MB |
| Modelo de embedding (`nomic-embed-text-v1.5` GGUF) | ~60 MB |
| LLM leve (`TinyLlama-1.1B` Q4_K_M) | ~700 MB |
| LLM médio (`Phi-3-mini-4k-instruct` Q4_K_M) | ~2,4 GB |
| **Total (leve)** | **~880 MB** |
| **Total (médio)** | **~2,6 GB** |

---

## O Que Precisa Ser Feito

### 1. Backend — Substituir Ollama por `llama-cpp-python`

**Arquivo alvo:** `backend/app/infra/llm.py`

Mudar de:
```python
# LLMFactory usa langchain_ollama / httpx pra chamar o Ollama
```

Para:
```python
from llama_cpp import Llama

class LLMFactory:
    @staticmethod
    def get_llm():
        return Llama(
            model_path="models/modelo.gguf",
            n_ctx=4096,
            n_threads=4,
            verbose=False,
        )
```

**Detalhes:**
- Precisa de 2 modelos GGUF: um pra embedding (`nomic-embed-text-v1.5.f16.gguf`) e um pra geração
- Embedding: o `llama-cpp-python` expõe `llama.create_embedding()`
- A classe `BatchedOllamaEmbeddings` em `backend/app/rag/embeddings.py` precisa ser adaptada
- O retriever do LangChain usa `embedding_function` — precisa de um wrapper compatível

### 2. Backend — Adaptar `embeddings.py`

**Arquivo alvo:** `backend/app/rag/embeddings.py`

O código atual tem `BatchedOllamaEmbeddings` que chama o Ollama via HTTP.
Precisa virar algo como:
```python
class LlamaCppEmbeddings:
    def __init__(self, model_path: str):
        self.llm = Llama(model_path=model_path, embedding=True)
    
    def embed_documents(self, texts):
        return [self.llm.create_embedding(t)["data"][0]["embedding"] for t in texts]
    
    def embed_query(self, text):
        return self.llm.create_embedding(text)["data"][0]["embedding"]
```

E a função `get_embeddings()` retornar uma instância disso.

### 3. Backend — Simplificar ou remover `LLMFactory`

Se `llama-cpp-python` vira o provedor único, pode remover a fábrica com lógica de Ollama e deixar uma inicialização direta.

### 4. PyInstaller — Configurar spec

Criar `sector-rag.spec` com:
- Entry point: `backend/app/main.py` (ou um launcher customizado)
- Data files: pasta `frontend/dist/` (build do React)
- Data files: pasta `models/` com os .gguf (opcional — pode baixar na 1ª execução)
- Hidden imports: `chromadb`, `llama_cpp`, `uvicorn`, `langchain`, etc
- Opção `--onefile` ou `--onedir`

### 5. Frontend — Build estático

Já funciona com `npm run build`. O PyInstaller vai embarcar a pasta `frontend/dist/` e o backend servirá os arquivos estáticos via FastAPI.

**Se o FastAPI ainda não serve estáticos**, adicionar em `backend/app/main.py`:
```python
from fastapi.staticfiles import StaticFiles
app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="frontend")
```

### 6. Launcher (opcional)

Um `main.py` simplificado que:
1. Descobre o caminho do executável (pra achar models/ e frontend/dist/)
2. Inicia o Uvicorn
3. Abre o browser em `http://localhost:8000`

---

## Comando Sugerido pra Abrir o Prompt

Quando for retomar, cole isso no início do prompt:

```
Continuar o plano de empacotamento do Sector-RAG.
Ver arquivo plano-pacote.md para contexto completo.
Objetivo: substituir Ollama por llama-cpp-python e empacotar com PyInstaller.
Comece pelo backend/app/infra/llm.py e backend/app/rag/embeddings.py.
```

---

## Ordem de Trabalho Sugerida

| Passo | Tarefa | Arquivos |
|---|---|---|
| 1 | Substituir Ollama por `llama-cpp-python` no LLMFactory | `backend/app/infra/llm.py` |
| 2 | Adaptar embeddings para `llama-cpp-python` | `backend/app/rag/embeddings.py` |
| 3 | Ajustar configuração (caminho dos modelos .gguf) | `backend/app/config.py` |
| 4 | Servir frontend estático pelo FastAPI | `backend/app/main.py` |
| 5 | Testar: `uvicorn` rodando tudo local (sem Ollama) | — |
| 6 | Criar spec do PyInstaller | `sector-rag.spec` |
| 7 | Build + testar executável | — |
| 8 | (Opcional) InnoSetup / NSIS pra instalador | `installer.iss` |

---

## Observações Técnicas

- `llama-cpp-python` compila C++ nativo no `pip install` — demora uns 5–10 min na 1ª vez
- No Windows, precisa de **Visual C++ Build Tools** ou usar wheel pré-compilado
- O PyInstaller vai gerar um executável de ~120 MB (contém Python + todas as libs)
- Os modelos GGUF ficam SEPARADOS (muito grandes pra embutir)
- ChromaDB é Python puro + SQLite → vai dentro do executável sem problema
- O banco vetorial (dados do usuário) fica em `./chroma_data/` — fora do executável
