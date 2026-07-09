from pydantic import BaseModel


class Source(BaseModel):
    content: str
    metadata: dict


class AskResponse(BaseModel):
    answer: str
    sources: list[Source]


class AskRequest(BaseModel):
    question: str
    sector: str


class UploadResponse(BaseModel):
    message: str
    documents_processed: int


class ClearSectorRequest(BaseModel):
    sector: str


class ChunkInfo(BaseModel):
    id: str
    content: str
    metadata: dict
