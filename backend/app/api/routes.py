"""Agregador de rotas + health check."""

from pydantic import BaseModel
from fastapi import APIRouter
from app.rag.routes import router as rag_router
from app.rag.vector_store import get_vector_store_adapter
from app.config import settings


class HealthResponse(BaseModel):
    status: str = "ok"
    app: str
    version: str
    vector_collections: list[str]


router = APIRouter()
router.include_router(rag_router)


@router.get("/health", response_model=HealthResponse)
def health_check():
    """Health check do servico."""
    store = get_vector_store_adapter()
    return HealthResponse(
        status="ok",
        app=settings.app_name,
        version=settings.app_version,
        vector_collections=store.list_collections(),
    )
