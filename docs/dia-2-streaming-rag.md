#  Dia 2 — Streaming no RAG + Limpeza do Código

> **Data:** 04/07/2026
> **Projeto original:** `rag-local` | **Fork:** `sector-rag`
> *Nota: Este documento é do projeto original. No Sector-RAG, o streaming SSE funciona com `POST /ask/stream` e exige o campo `sector` no body.*

---

##  O que foi feito

Implementação de streaming token a token no endpoint do RAG (`/ask/stream`) e limpeza geral do código removendo perfumaria desnecessária.

##  Limpeza do código

### Removido

| Módulo | Motivo |
|--------|--------|
| `app/observability/` | structlog + OpenTelemetry — perfumaria, desnecessário pro projeto |
| `app/memory/` | Wrapper não utilizado (agente já usava `MemorySaver` diretamente) |
| `asynccontextmanager` + `lifespan` | Em `main.py` — era só pra logar "iniciou" e "encerrou" |
| `otlp_endpoint` | Em `config.py` — só existia pro OpenTelemetry |
| structlog, opentelemetry, rich | Dependências removidas do `requirements.txt` |

### Simplificado

| Arquivo | Antes | Depois |
|---------|-------|--------|
| `app/main.py` | 52 linhas (lifespan, logging, imports) | 30 linhas, só o essencial |
| `app/config.py` | 29 linhas (com `otlp_endpoint`) | 25 linhas, só o que usa |
| `requirements.txt` | 38 linhas (structlog, opentelemetry, rich, etc) | 27 linhas, só o necessário |

### Estrutura final

```
app/
├── main.py              ← 30 linhas, enxuto
├── config.py            ← Settings simplificado
├── api/
│   ├── routes.py        ← 5 rotas (+ /ask/stream)
│   └── schemas.py
├── rag/
│   ├── engine.py        ← ask() + ask_stream()
│   ├── embeddings.py
│   └── vectorstore.py
├── agents/
│   ├── agent.py
│   └── tools.py
└── mcp/
    └── server.py
```

---

##  Streaming no RAG

### `engine.py` — `ask_stream()`

```python
def ask_stream(question: str):
    """Pergunta ao RAG e retorna generator com tokens um por um."""
    docs = retriever.invoke(question)
    context = "\n\n".join(doc.page_content for doc in docs)
    prompt = SYSTEM_PROMPT.format(context=context, input=question)
    for chunk in llm.stream(prompt):
        if chunk.content:
            yield chunk.content
```

### Formato SSE

```
data: {"token": "Com"}
data: {"token": " base"}
data: {"token": " nos"}
data: {"token": " documentos"}
...
data: [DONE]
```

---

##  Resumo das mudanças

| Arquivo | Mudança |
|---------|---------|
| `app/rag/engine.py` | + `ask_stream()` — generator de tokens |
| `app/api/routes.py` | + `POST /ask/stream` com SSE |
| `app/main.py` | Simplificado (sem lifespan, sem observability) |
| `app/config.py` | Removido `otlp_endpoint` |
| `requirements.txt` | Removido structlog, opentelemetry, rich, sentence-transformers, unstructured |
| `app/observability/` |  Removido |
| `app/memory/` |  Removido |

---

##  Como testar

```bash
curl -N -X POST http://localhost:8000/api/v1/ask/stream \
  -H "Content-Type: application/json" \
  -d '{"question": "O que diz o documento?"}'
```

---

##  Observações

- Código foi enxugado pensando em **manutenibilidade** — cliente precisa entender
- Remoção de `observability/` e `memory/` reduziu complexidade sem perder funcionalidade
- Streaming usa SSE (Server-Sent Events), formato leve e compatível com qualquer frontend
