"""FastAPI App — Sector-RAG (RAG setorial)."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.routes import router

logger = logging.getLogger(__name__)

app = FastAPI(title=settings.app_name, version=settings.app_version)

# ── CORS — libera geral pra desenvolvimento ────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Rotas REST ────────────────────────────────────────────────────────
app.include_router(router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
