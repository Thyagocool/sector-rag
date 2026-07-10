"""Rotas do RAG — apenas roteamento, logica delegada aos use cases."""

import json
import logging
import tempfile
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query
from fastapi.responses import StreamingResponse

from app.rag.schemas import (
    AskRequest,
    AskResponse,
    Source,
    UploadResponse,
    ClearSectorRequest,
    ChunkInfo,
    FileInfo,
    FileTopic,
    SubTopic,
    TopicChunk,
    TopicChunksResponse,
)
from app.config import settings
from app.rag.use_cases.ask_use_case import AskUseCase
from app.rag.use_cases.document_use_case import DocumentUseCase
from app.rag.vector_store import get_vector_store_adapter


logger = logging.getLogger(__name__)

ask_uc = AskUseCase()
document_uc = DocumentUseCase()

_MAX_UPLOAD_BYTES = settings.max_upload_size_mb * 1024 * 1024

router = APIRouter()


# ─── Helpers de streaming ───────────────────────────────────────────────


def _stream_answer(
    question: str,
    sector: str,
    source: str | None = None,
    topic: str | None = None,
    subtopic: str | None = None,
):
    """Converte tokens do RAG em eventos SSE."""
    try:
        for token in ask_uc.ask_stream(question, sector, source=source, topic=topic, subtopic=subtopic):
            yield f"data: {json.dumps({'token': token})}\n\n"
    except Exception as e:
        logger.exception("Erro no streaming para setor '%s'", sector)
        yield f"data: {json.dumps({'error': str(e)})}\n\n"
    finally:
        yield "data: [DONE]\n\n"


# ─── Rotas do RAG ──────────────────────────────────────────────────────


@router.post("/ask", response_model=AskResponse)
def ask_rag(payload: AskRequest):
    """Faz uma pergunta ao RAG com filtros opcionais (setor, source, topic, subtopic)."""
    try:
        result = ask_uc.ask(
            payload.question,
            payload.sector,
            source=payload.source,
            topic=payload.topic,
            subtopic=payload.subtopic,
        )
        return AskResponse(
            answer=result["answer"],
            sources=[Source(**s) for s in result["sources"]],
        )
    except Exception as e:
        logger.exception("Erro no /ask para setor '%s'", payload.sector)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ask/stream")
def ask_rag_stream(payload: AskRequest):
    """Faz uma pergunta ao RAG com resposta em streaming (SSE)."""
    return StreamingResponse(
        _stream_answer(
            payload.question,
            payload.sector,
            source=payload.source,
            topic=payload.topic,
            subtopic=payload.subtopic,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/upload", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    sector: str = Form("geral"),
):
    """Faz upload de um documento para indexar no RAG em um setor."""
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

    import time
    t0 = time.time()

    try:
        t1 = time.time()
        chunks = document_uc.load_and_chunk(Path(tmp_path), sector=sector, source_name=file.filename)
        t2 = time.time()
        logger.info("Upload: load_and_chunk de %s levou %.1fs (%d chunks)", file.filename, t2 - t1, len(chunks))

        document_uc.ingest_documents(chunks)
        t3 = time.time()
        logger.info("Upload: ingestão de %d chunks levou %.1fs", len(chunks), t3 - t2)
        logger.info("Upload TOTAL: %.1fs", t3 - t0)

        return UploadResponse(
            message=f"{file.filename} indexado no setor '{sector}' com sucesso!",
            documents_processed=len(chunks),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        Path(tmp_path).unlink(missing_ok=True)


# ─── Rotas de Setor ─────────────────────────────────────────────────────


@router.get("/sector/files", response_model=list[FileInfo])
def list_sector_files(sector: str = Query(...)):
    """Lista os arquivos de um setor com árvore de tópicos e subtópicos."""
    store = get_vector_store_adapter()
    files_data = store.get_files_by_sector(sector)
    result = []
    for fdata in files_data:
        # Agrupa chunks por topic → subtopic
        topics_map: dict[str, dict] = {}
        for chunk in fdata["chunks"]:
            topic = chunk["metadata"].get("topic", "") or "Sem título"
            subtopic = chunk["metadata"].get("subtopic", "") or chunk["content"][:70]

            if topic not in topics_map:
                topics_map[topic] = {
                    "snippet": chunk["content"][:120],
                    "subs": {},
                }
            if subtopic not in topics_map[topic]["subs"]:
                topics_map[topic]["subs"][subtopic] = chunk["content"]

        topics_list = []
        for topic_name, tdata in topics_map.items():
            sub_list = [
                SubTopic(subtopic=sname, snippet=content[:120], content=content)
                for sname, content in tdata["subs"].items()
            ]
            topics_list.append(FileTopic(
                topic=topic_name,
                snippet=tdata["snippet"],
                subtopics=sub_list,
            ))

        result.append(FileInfo(filename=fdata["filename"], topics=topics_list))
    return result


@router.get("/sector/topic/chunks", response_model=TopicChunksResponse)
def list_topic_chunks(
    sector: str = Query(...),
    file: str = Query(..., alias="file"),
    topic: str = Query(...),
):
    """Retorna os chunks de um tópico específico dentro de um arquivo."""
    store = get_vector_store_adapter()
    chunks_data = store.get_chunks_by_topic(sector, file, topic)
    return TopicChunksResponse(
        topic=topic,
        chunks=[TopicChunk(chunk_id=c["id"], content=c["content"]) for c in chunks_data],
    )


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
