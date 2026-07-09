# Sector-RAG — RAG Setorial

> Fork do projeto `rag-local`, adaptado para um RAG departamental/setorial.
> Sem agentes, sem MCP — só RAG puro com filtro por setor.

---

## Contexto

- **Projeto original:** `rag-local` — RAG + Agentes + MCP + Frontend
- **Fork:** `sector-rag` — RAG puro, cada documento pertence a um setor
- **Stack:** FastAPI + LangChain + ChromaDB + Ollama + React
- **Diferencial:** Usuário informa o setor no upload; consulta filtra por setor

---

## O que já vem do original

- Backend: FastAPI + LangChain + ChromaDB + Ollama
- Frontend: React 19 + Vite 8 + TypeScript 6
- RAG: upload, chunking (4 estratégias), ask, streaming SSE
- Vector Store: ChromaDB com Adapter Pattern
- Chunking: Strategy Pattern (recursivo, markdown, código, semântico)
- Reranking: cross-encoder (opcional)
- Deploy: Docker Compose + Nginx + host-ollama

---

## O que foi removido

- Agentes (LangGraph, tools, web_search)
- MCP Server (stdio + SSE)
- Tracing / OpenTelemetry
- Opção "Agent" no frontend
- Dependências não utilizadas

---

## O que será adicionado

| Funcionalidade | Descrição |
|----------------|-----------|
| Upload com setor | Usuário informa o setor (ex: "RH", "Jurídico") ao subir o arquivo |
| Pergunta por setor | Usuário seleciona/ informa o setor antes de perguntar |
| Filtro no ChromaDB | Busca vetorial filtrada por metadado `sector` |
| Seletor de setor | Tela inicial do frontend pergunta "Qual setor?" |
| Painel Admin | Lista setores, exibe chunks, permite limpar por setor |
| Troca de setor | Usuário pode trocar de setor sem recarregar a página |

---

## Roteiro

```
Fase 0 — Fork + setup do projeto                   🔄 EM ANDAMENTO
Fase 1 — Remover agente, MCP, tracing do backend   ⏳ PENDENTE
Fase 1 — Remover agente do frontend                ⏳ PENDENTE
Fase 2 — Setores no backend (schemas, upload, ask) ⏳ PENDENTE
Fase 3 — Frontend: seletor de setor + admin         ⏳ PENDENTE
Fase 4 — Ajustes finais + docs + deploy             ⏳ PENDENTE
```

---

## Como rodar

```bash
# Opção 1 — Docker completo
cd backend
docker compose up --build

# Opção 2 — Ollama no host (recomendado para servidores com pouca RAM)
docker compose -f docker-compose.host-ollama.yml up -d --build

# Opção 3 — Desenvolvimento
docker compose up -d ollama
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
