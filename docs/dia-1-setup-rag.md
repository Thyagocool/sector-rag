#  Dia 1 — Setup + RAG funcional

> **Data:** 30/06/2026
> **Branch:** `main`

---

##  O que foi feito

Revisão completa do projeto, correção de bugs, setup do ambiente e primeira execução do RAG.

### Setup do ambiente

| Componente | Configuração |
|------------|-------------|
| **API** | FastAPI rodando via `uvicorn --reload` |
| **LLM** | Ollama no Docker (`llama3.2:3b`) |
| **Embeddings** | Ollama (`nomic-embed-text`) |
| **Vector Store** | ChromaDB persistente em `./data/chroma` |
| **Portas** | API `:8000`, Ollama `:11434` |

### Estrutura do projeto (8 módulos)

```
app/
├── main.py              → FastAPI app
├── config.py            → Settings (Pydantic)
├── api/
│   ├── routes.py        → Endpoints REST
│   └── schemas.py       → Schemas Pydantic
├── rag/
│   ├── engine.py        → Motor RAG (ask, ingest, clear)
│   ├── embeddings.py    → Embeddings via Ollama
│   └── vectorstore.py   → ChromaDB wrapper
├── agents/
│   ├── agent.py         → LangGraph (grafo agente)
│   └── tools.py         → 4 ferramentas
├── mcp/
│   └── server.py        → Servidor MCP via stdio
├── observability/
│   └── logging.py       → structlog (removido no Dia 2)
└── memory/
    └── memory.py        → Checkpointer (removido no Dia 2)
```

### Endpoints iniciais

| Método | Rota | Descrição |
|--------|------|-----------|
| `POST` | `/api/v1/ask` | Pergunta ao RAG |
| `POST` | `/api/v1/upload` | Upload de documento |
| `DELETE` | `/api/v1/clear` | Limpa banco vetorial |
| `POST` | `/api/v1/agent` | Conversa com agente |
| `GET` | `/api/v1/health` | Health check |

### Correções aplicadas

-  `observability/logging.py` — structlog configurado com `PrintLogger` (sem `filter_by_level`/`add_logger_name`)
-  `main.py` — f-string no lugar de printf-style (`%s`)
-  `docker-compose.yml` — `OLLAMA_HOST` adicionado ao container `ollama-init`

### Tools do Agente (LangGraph)

| Tool | Descrição |
|------|-----------|
| `search_documents` | Busca no RAG |
| `get_current_time` | Data/hora atual |
| `calculate` | Expressões matemáticas |
| `list_available_tools` | Auto-descrição |

---

##  Como testar

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Upload
curl -X POST http://localhost:8000/api/v1/upload \
  -F "file=@documento.pdf"

# Pergunta
curl -X POST http://localhost:8000/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "O que diz o documento?"}'
```

---

##  Observações

- Projeto 100% local (Ollama), sem custos de API
- RAG testado e respondendo pelo Swagger
- Estrutura com 8 módulos (alguns removidos no Dia 2 por serem perfumaria)
