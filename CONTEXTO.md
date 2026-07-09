# Contexto da Sessão — Sector-RAG

## Projeto
- Fork do `rag-local`, renomeado para **Sector-RAG**
- Pasta: `/home/thyago/Dev/sector-rag` (ou onde clonou)
- RAG puro, **sem agentes, sem MCP, sem tracing**
- Stack: FastAPI + LangChain + ChromaDB + Ollama + React
- Repo: [github.com/Thyagocool/sector-rag](https://github.com/Thyagocool/sector-rag)

## O que já foi feito

### Backend
- Removido: `app/agents/`, `app/mcp/`, `app/infra/tracing.py`
- `config.py`: app_name="Sector-RAG", modelo qwen2.5:0.5b, reranking false
- `rag/schemas.py`: AskRequest com `sector`, ClearSectorRequest, ChunkInfo
- `rag/routes.py`:
  - POST /upload — recebe `file` + `sector` (form field)
  - POST /ask e /ask/stream — recebem `question` + `sector`
  - GET /sectors — lista setores únicos
  - GET /admin/chunks?sector=... — lista chunks de um setor
  - DELETE /admin/chunks — body `{"sector": "..."}`
- `rag/use_cases/ask_use_case.py`: `_retrieve()` filtra por `{"sector": sector}`
- `rag/use_cases/document_use_case.py`: `load_and_chunk()` adiciona metadata `{"sector": ..., "source": ...}`
- `rag/vector_store/protocol.py`: novos métodos abstratos `list_sectors()`, `get_chunks_by_sector()`, `delete_by_sector()`
- `rag/vector_store/chroma_adapter.py`: implementa os 3 novos métodos com `where={"sector": sector}`
- `requirements.txt`: limpo (sem langgraph, mcp, ddgs, opentelemetry)

### Frontend
- `App.tsx`: estado `sector` + `view` (chat|admin), sem mode toggle
- `SectorSelector.tsx`: tela inicial que pergunta o setor
- `Header.tsx`: sem modo agente, sem clear, mostra "Setor: {sector}", botões Upload/Admin/Trocar setor
- `Chat.tsx`: só RAG, recebe `sector`, chama API com sector
- `AdminPanel.tsx`: lista chunks do setor, botão "Limpar setor"
- `api.ts`: funções com sector, + listSectors, listChunks, clearSector
- CSS: novos estilos para sector-selector, admin-panel, admin-chunks

### Docker
- `docker-compose.yml` (raiz): stack completa com frontend
- `docker-compose.host-ollama.yml`: pra servidor com pouca RAM
- `backend/docker-compose.yml`: dev
- `backend/docker-compose.prod.yml`: produção com Nginx + limites

### Docs mantidos
- `docs/dia-1-setup-rag.md`
- `docs/dia-2-streaming-rag.md`
- `docs/dia-4-chunking-esperto.md`
- `docs/dia-5-reranking.md`

### Modelo LLM
- qwen2.5:0.5b (~400MB, 494M params)
- Reranking desabilitado
- Ollama nomic-embed-text pra embeddings

### Publicação
- Repositório criado no GitHub: `Thyagocool/sector-rag`
- Remote origin configurada e push realizado

## Pendências / Ideias
- [ ] Testar upload + pergunta com setor no servidor remoto
- [ ] Post do LinkedIn sobre o RAG original (texto já pronto na sessão)
