# Dia 5 — Reranking (melhorar qualidade das respostas)

## O que foi feito

### Problema
O RAG busca documentos por similaridade vetorial (cosine similarity no embedding).
Isso pode trazer documentos com "terna parecido" mas que nao respondem a pergunta de fato.
O resultado: respostas com contexto irrelevante ou ate errado.

### Solucao: Cross-Encoder Reranker

Em vez de confiar so no similarity search, a gente:

1. **Busca mais documentos** (k=10 em vez de k=4)
2. **Re-ordena** com um modelo cross-encoder que avalia a relevancia de cada documento *em relacao a pergunta*
3. **Pega os top_k** (4) mais relevantes

### O modelo

Usamos `cross-encoder/ms-marco-MiniLM-L-2-v2` da HuggingFace:
- Tamanho: ~80MB
- Roda em CPU tranquilo
- Otimizado para ranking de relevancia pergunta-documento

### Arquivos criados

```
app/rag/reranking/
├── __init__.py
└── reranker.py    ← CrossEncoder wrapper com cache singleton
```

### API publica

```python
from app.rag.reranking import rerank

docs_reranked = rerank(
    query="Qual a temperatura maxima?",
    documents=docs_brutos,  # list[Document]
    top_k=4,                # quantos devolver
)
```

### Integracao com AskUseCase

- `AskUseCase` agora aceita `use_reranking` no construtor (default = config)
- Config: `RAG_RERANKING_ENABLED=True` (env var)
- Quando ativo, busca k=10 e re-ordena pra k=4
- Quando desativo, busca k=4 diretamente (comportamento original)

### Configuracao (app/config.py)
```python
rag_reranking_enabled: bool = True
rag_reranking_top_k: int = 4
```

Pode desabilitar via env var:
```bash
export RAG_RERANKING_ENABLED=false
```

## Como testar

O reranking eh transparente pro usuario — so perguntar normal:

```bash
curl -X POST http://localhost:8000/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "O que diz o documento sobre temperatura?"}'
```

Se quiser ver a diferenca, desabilite o reranking e compare:
```bash
# Com reranking (padrao)
# Sem reranking — mude a config ou inicie com env var
RAG_RERANKING_ENABLED=false uvicorn app.main:app --reload
```

## Proximos passos
- Testar modelos maiores de cross-encoder (melhor precisao, mais lento)
- Adicionar cache de scores para perguntas similares
- Logging dos scores no response para debug
