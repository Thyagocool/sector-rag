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
    source: str | None = None
    topic: str | None = None
    subtopic: str | None = None


class UploadResponse(BaseModel):
    message: str
    documents_processed: int


class ClearSectorRequest(BaseModel):
    sector: str


class ChunkInfo(BaseModel):
    id: str
    content: str
    metadata: dict


class SubTopic(BaseModel):
    """Subtópico (nível 2) dentro de um tópico."""
    subtopic: str
    snippet: str
    content: str = ""


class FileTopic(BaseModel):
    topic: str
    snippet: str
    subtopics: list[SubTopic] = []


class FileInfo(BaseModel):
    filename: str
    topics: list[FileTopic]


class TopicChunk(BaseModel):
    """Um chunk individual dentro de um tópico."""
    chunk_id: str
    content: str

    class Config:
        # Permite nomes de campo com snake_case vindos do Python
        populate_by_name = True


class TopicChunksResponse(BaseModel):
    """tópico com seus chunks."""
    topic: str
    chunks: list[TopicChunk]
