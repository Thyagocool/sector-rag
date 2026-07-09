# =============================================================================
# Dockerfile — RAG + Agentes + MCP (produção)
# Multi-stage build com usuário não-root, healthcheck e imagem otimizada.
# =============================================================================

# ─── Stage 1: Builder ────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

# Apenas dependências do sistema necessárias para compilar pacotes
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    find /usr/local -name '*.pyc' -delete && \
    find /usr/local -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true

# ─── Stage 2: Runtime (imagem final enxuta) ─────────────────────────────────
FROM python:3.12-slim

# Meta-info
LABEL maintainer="Thyago"
LABEL description="RAG + Agentes + MCP — API local de IA"
LABEL version="0.1.0"

# Ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    RAG_DEBUG=false

WORKDIR /app

# Apenas curl para healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copia apenas site-packages do builder (sem binarios desnecessarios)
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

# Cria diretório de dados do ChromaDB (para volume persistente)
RUN mkdir -p /data/chroma

# Cria usuário não-root para segurança
RUN addgroup --system --gid 1001 app && \
    adduser --system --uid 1001 --ingroup app app && \
    chown -R app:app /app && \
    chown -R app:app /data/chroma

# Copia o código (com ownership pro usuário app)
COPY --chown=app:app . .

# Remove arquivos desnecessários pra enxugar a imagem
RUN find /app -name '*.pyc' -delete && \
    find /app -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true

# Expõe a porta da API
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -sf http://localhost:8000/api/v1/health || exit 1

# Muda para usuário não-root
USER app

# Comando padrão
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
