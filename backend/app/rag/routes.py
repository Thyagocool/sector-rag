"""Rotas do RAG — apenas roteamento, logica delegada aos use cases."""

import json
import tempfile
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import StreamingResponse

from app.rag.schemas import (
    AskRequest,
    AskResponse,
    Source,
    UploadResponse,
    ClearSectorRequest,
    ChunkInfo,
)
from app.config import settings
from app.rag.use_cases.ask_use_case import AskUseCase
from app.rag.use_cases.document_use_case import DocumentUseCase
from app.rag.vector_store import get_vector_store_adapter


ask_uc = AskUseCase()
document_uc = DocumentUseCase()

_MAX_UPLOAD_BYTES = settings.max_upload_size_mb * 1024 * 1024

router = APIRouter()


# ─── Helpers de streaming ───────────────────────────────────────────────


def _stream_answer(question: str, sector: str):
    """Converte tokens do RAG em eventos SSE."""
    for token in ask_uc.ask_stream(question, sector):
        yield f"data: {json.dumps({'token': token})}\n\n"
    yield "data: [DONE]\n\n"


# ─── Rotas do RAG ──────────────────────────────────────────────────────


@router.post("/ask", response_model=AskResponse)
def ask_rag(payload: AskRequest):
    """Faz uma pergunta ao RAG com base nos documentos indexados do setor."""
    try:
        result = ask_uc.ask(payload.question, payload.sector)
        return AskResponse(
            answer=result["answer"],
            sources=[Source(**s) for s in result["sources"]],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ask/stream")
def ask_rag_stream(payload: AskRequest):
    """Faz uma pergunta ao RAG com resposta em streaming (SSE)."""
    return StreamingResponse(
        _stream_answer(payload.question, payload.sector),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/upload", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    sector: str = "geral",
):
    """Faz upload de um documento para indexar no RAG em um setor.

    O parametro 'sector' pode vir como query param ou campo Form.
    """
    sector = sector.strip() or "geral"

    if file.filename is None:
        raise HTTPException(status_code=400, detail="Filename nao informado")

    ext = Path(file.filename).suffix.lower()
    if ext not in document_uc.SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Formato nao suportado: {ext}. "
                f"Use: {', '.join(sorted(document_uc.SUPPORTED_EXTENSIONS))}"
            ),
        )

    content = await file.read()
    if len(content) > _MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"Arquivo muito grande. Maximo: {settings.max_upload_size_mb}MB",
        )

    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        chunks = document_uc.load_and_chunk(Path(tmp_path), sector=sector)
        document_uc.ingest_documents(chunks)
        return UploadResponse(
            message=f"{file.filename} indexado no setor '{sector}' com sucesso!",
            documents_processed=len(chunks),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        Path(tmp_path).unlink(missing_ok=True)


# ─── Rotas de Admin ─────────────────────────────────────────────────────


@router.get("/sectors")
def list_sectors():
    """Lista todos os setores que possuem documentos indexados."""
    store = get_vector_store_adapter()
    return store.list_sectors()


@router.get("/admin/chunks")
def list_chunks_by_sector(sector: str = Query(...)):
    """Lista todos os chunks de um setor."""
    store = get_vector_store_adapter()
    chunks = store.get_chunks_by_sector(sector)
    return [ChunkInfo(id=c["id"], content=c["content"], metadata=c["metadata"]) for c in chunks]


@router.delete("/admin/chunks")
def delete_chunks_by_sector(payload: ClearSectorRequest):
    """Remove todos os chunks de um setor."""
    store = get_vector_store_adapter()
    store.delete_by_sector(payload.sector)
    return {"message": f"Setor '{payload.sector}' limpo com sucesso!"}
