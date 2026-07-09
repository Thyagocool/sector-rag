#  Sector-RAG — RAG Departamental/Setorial

**API de RAG puro (sem agentes, sem MCP) com filtro por setor** — cada documento pertence a um setor (ex: "RH", "Jurídico", "TI") e as consultas só enxergam o setor selecionado. Tudo 100% local e grátis com Ollama.

> Stack: **FastAPI + LangChain + ChromaDB + Ollama + React**  
> Frontend: **React 19 + Vite 8 + TypeScript 6**  
> Modelo leve: **Qwen 2.5 0.5B** (~400MB) — roda até em servidores com **1GB de RAM**

---

##  Funcionalidades

| Funcionalidade | Descrição |
|----------------|-----------|
| **Upload com setor** | Usuário informa o setor (ex: "RH", "Jurídico") ao subir o arquivo |
| **Pergunta por setor** | Usuário seleciona o setor antes de perguntar; a busca considera apenas documentos daquele setor |
| **Streaming SSE** | Respostas token a token |
| **Chunking inteligente** | 4 estratégias (recursivo, markdown, código, semântico) |
| **Seletor de setor** | Tela inicial do frontend pergunta "Qual setor?" |
| **Painel Admin** | Lista setores, exibe chunks, permite limpar por setor |
| **Troca de setor** | Usuário pode trocar de setor sem recarregar a página |
| **15 formatos de documento** | PDF, TXT, MD, DOCX, HTML, CSV, JSON, PY, JS, TS, SQL, YAML, XML |
| **100% local** | LLM e embeddings rodando via Ollama — sem API paga, sem dados saindo da sua máquina |

---

##  Stack

```
Frontend (React + Vite)          Backend (FastAPI)
       │                              │
       │  POST /api/v1/*              │
       │◄─────────────────────────────│
       │                              │
       │   SSE (Server-Sent Events)   │
       │◄─────────────────────────────│
       │                              │
       │                    ┌─────────┴─────────┐
       │                    │                   │
       │               ┌────┴────┐        ┌────┴────┐
       │               │ Ollama  │        │ChromaDB │
       │               │(LLM +   │        │(Vector  │
       │               │Embdds)  │        │ Store)  │
       │               └─────────┘        └─────────┘
```

---

##  ⚡ Início Rápido

### Opção 1 — Docker completo

```bash
docker compose up --build
# API → http://localhost:8000
# Swagger → http://localhost:8000/docs
# Frontend → http://localhost
```

### Opção 2 — Ollama no host + API em container (recomendado para servidores com pouca RAM)

```bash
# Ollama roda no host (fora do Docker), API + Frontend em container
docker compose -f docker-compose.host-ollama.yml up -d --build
# API → http://localhost:8000
```

### Opção 3 — Desenvolvimento (hot reload)

```bash
# Terminal 1: Ollama via Docker
cd backend
docker compose up -d ollama

# Terminal 2: API local
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Opção 4 — Frontend (dev)

```bash
# Terminal 1: Backend
cd backend && source venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd frontend && npm run dev
# Acessar: http://localhost:5173
```

---

##  Endpoints da API

### REST

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/api/v1/health` | Health check |
| `POST` | `/api/v1/ask` | Pergunta ao RAG (com `sector`) |
| `POST` | `/api/v1/ask/stream` | Pergunta ao RAG com streaming SSE (com `sector`) |
| `POST` | `/api/v1/upload` | Upload de documento (com `sector` via form field) |
| `GET` | `/api/v1/sectors` | Lista setores com documentos indexados |
| `GET` | `/api/v1/admin/chunks?sector=...` | Lista chunks de um setor |
| `DELETE` | `/api/v1/admin/chunks` | Remove todos os chunks de um setor |

### Teste rápido

```bash
# Health check
curl -s http://localhost:8000/api/v1/health | python3 -m json.tool

# Upload para o setor "rh"
curl -s -X POST http://localhost:8000/api/v1/upload \
  -F "file=@documento.pdf" \
  -F "sector=rh"

# Pergunta ao RAG no setor "rh"
curl -s -X POST http://localhost:8000/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "O que diz o documento?", "sector": "rh"}'

# Listar setores
curl -s http://localhost:8000/api/v1/sectors

# Listar chunks do setor "rh"
curl -s "http://localhost:8000/api/v1/admin/chunks?sector=rh"

# Limpar setor "rh"
curl -s -X DELETE http://localhost:8000/api/v1/admin/chunks \
  -H "Content-Type: application/json" \
  -d '{"sector": "rh"}'
```

---

##  Arquitetura

O projeto foi refatorado seguindo **SOLID**, **Clean Code** e **DRY**, aplicando padrões de projeto para garantir desacoplamento, testabilidade e manutenibilidade.

### Padrões utilizados

| Padrão | Onde | Pra quê |
|--------|------|---------|
| **Adapter** | `rag/vector_store/` | ChromaDB encapsulado atrás de `VectorStoreAdapter`. Troca o banco sem afetar o resto |
| **Strategy** | `rag/chunking/` | 4 estratégias de chunking (recursivo, markdown, código, semântico). Factory escolhe, use case consome |
| **Dependency Injection** | `rag/use_cases/` | `AskUseCase` recebe `VectorStoreAdapter`, `DocumentUseCase` recebe `ChunkingStrategy` |

### Estrutura de diretórios

```
backend/
├── app/
│   ├── api/routes.py            # Rotas REST (health, legacy)
│   ├── rag/
│   │   ├── routes.py            # Rotas do RAG (upload, ask, admin)
│   │   ├── schemas.py           # Schemas Pydantic (AskRequest, etc.)
│   │   ├── embeddings.py        # Embeddings via Ollama
│   │   ├── loaders.py           # Loaders para 15 formatos
│   │   ├── chunking/            # Strategy Pattern — 4 estrategias
│   │   ├── reranking/           # Cross-encoder reranking (opcional)
│   │   ├── vector_store/        # Adapter Pattern — ChromaDB
│   │   └── use_cases/
│   │       ├── ask_use_case.py      # Pergunta ao RAG (com DI)
│   │       └── document_use_case.py # Upload + chunk + ingest (com DI)
│   ├── config.py                # Pydantic Settings c/ env vars (RAG_ prefix)
│   └── main.py                  # FastAPI app
├── nginx/nginx.conf             # Reverse proxy (producao)
├── scripts/deploy.sh            # Script de deploy automatizado
├── docker-compose.yml           # Stack dev (sem frontend)
├── docker-compose.prod.yml      # Stack producao (Nginx + limites)
└── requirements.txt             # Dependencias

frontend/
├── src/
│   ├── components/
│   │   ├── Chat.tsx             # Chat setorial (streaming SSE)
│   │   ├── Header.tsx           # Header com setor, upload, admin
│   │   ├── SectorSelector.tsx   # Tela inicial — "Qual setor?"
│   │   └── AdminPanel.tsx       # Admin: lista chunks, limpa setor
│   ├── services/
│   │   └── api.ts               # Camada de API (com sector)
│   ├── App.tsx                  # Componente principal
│   └── main.tsx                 # Entry point
└── ...

docs/                            # Documentacao do desenvolvimento
```

---

##  Configuração

Variáveis de ambiente com prefixo `RAG_`:

| Variável | Default | Descrição |
|----------|---------|-----------|
| `RAG_OLLAMA_BASE_URL` | `http://localhost:11434` | URL do Ollama |
| `RAG_LLM_MODEL` | `qwen2.5:0.5b` | Modelo de linguagem (~400MB, roda em 1GB RAM) |
| `RAG_EMBEDDING_MODEL` | `nomic-embed-text` | Modelo de embeddings |
| `RAG_CHROMA_PERSIST_DIR` | `./data/chroma` | Diretório do ChromaDB |
| `RAG_COLLECTION_NAME` | `rag_docs` | Nome da coleção vetorial |
| `RAG_DEBUG` | `true` | Modo debug |
| `RAG_RERANKING_ENABLED` | `false` | Reranking (requer sentence-transformers) |

---

##  Formatos de Documento Suportados

`PDF`, `TXT`, `MD`, `DOCX`, `HTML`, `CSV`, `JSON`, `PY`, `JS`, `TS`, `SQL`, `YAML`, `XML`

---

##  Como usar

1. **Escolha um setor** na tela inicial (ex: "jurídico", "rh", "ti")
2. **Faça upload** de documentos para aquele setor
3. **Faça perguntas** — o RAG só busca nos documentos do setor selecionado
4. **Administre** pelo painel admin: veja os chunks ou limpe o setor
5. **Troque de setor** a qualquer momento sem recarregar a página

---

##  Licença

MIT — sinta-se livre pra usar, estudar e modificar.
