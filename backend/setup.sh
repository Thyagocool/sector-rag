#!/usr/bin/env bash
# =============================================================================
# Setup automático do projeto RAG + Agentes + MCP
# =============================================================================
set -euo pipefail

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║      Setup RAG + Agentes + MCP - Tudo local e grátis     ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# ─── 1. Python virtual env ─────────────────────────────────────────────────
echo "[1/5] Criando ambiente virtual Python..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "   venv criado"
else
    echo "  [skip] venv ja existe"
fi

source venv/bin/activate

# ─── 2. Dependências ───────────────────────────────────────────────────────
echo "[2/5] Instalando dependências..."
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
echo "   Dependências instaladas"

# ─── 3. Ollama ─────────────────────────────────────────────────────────────
echo "[3/5] Verificando Ollama..."
if command -v ollama &> /dev/null; then
    echo "   Ollama encontrado!"
    
    echo "  Baixando modelo de linguagem (llama3.2:3b)..."
    ollama pull llama3.2:3b 2>/dev/null || true
    
    echo "  Baixando modelo de embeddings (nomic-embed-text)..."
    ollama pull nomic-embed-text 2>/dev/null || true
    
    echo "  Modelos prontos!"
else
    echo "  Ollama nao encontrado."
    echo "  Instale com: curl -fsSL https://ollama.com/install.sh | sh"
    echo "  Ou rode com Docker: docker compose up -d ollama"
fi

# ─── 4. Diretórios ─────────────────────────────────────────────────────────
echo "[4/5] Criando diretórios de dados..."
mkdir -p data/chroma
echo "  data/chroma criado"

# ─── 5. .env ───────────────────────────────────────────────────────────────
echo "[5/5] Configurando .env..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "  .env criado a partir do .env.example"
else
    echo "  [skip] .env ja existe"
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║   Setup completo!                                          ║"
echo "║                                                              ║"
echo "║  Para rodar a API:                                           ║"
echo "║    source venv/bin/activate                                  ║"
echo "║    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 ║"
echo "║                                                              ║"
echo "║  Para rodar o MCP server:                                    ║"
echo "║    source venv/bin/activate                                  ║"
echo "║    python -m app.mcp.server                                  ║"
echo "║                                                              ║"
echo "║  Endpoints:                                                  ║"
echo "║     POST /api/v1/upload  - Upload de documento            ║"
echo "║     POST /api/v1/ask     - Pergunta ao RAG                ║"
echo "║     POST /api/v1/agent   - Conversa com agente            ║"
echo "║      GET  /api/v1/health  - Health check                  ║"
echo "╚══════════════════════════════════════════════════════════════╝"
