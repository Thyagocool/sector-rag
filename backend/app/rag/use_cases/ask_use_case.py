"""Use case: fazer perguntas ao RAG (normal e streaming) com filtro por setor."""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from app.infra.llm import LLMFactory
from app.rag.vector_store import VectorStoreAdapter, get_vector_store_adapter
from app.config import settings
import logging

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Você é um assistente que responde perguntas com base em documentos fornecidos no contexto abaixo."""
USER_PROMPT = """Contexto:
{context}

Pergunta: {input}"""

RETRIEVAL_PROMPT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", USER_PROMPT),
])


class AskUseCase:
    """Pergunta ao RAG — com filtro por setor."""

    def __init__(
        self,
        vector_store: VectorStoreAdapter | None = None,
    ):
        self._llm = None
        self._vector_store = vector_store

    def _get_llm(self):
        if self._llm is None:
            self._llm = LLMFactory.get_llm()
        return self._llm

    def _get_store(self) -> VectorStoreAdapter:
        if self._vector_store is None:
            self._vector_store = get_vector_store_adapter()
        return self._vector_store

    def _retrieve(
        self,
        question: str,
        sector: str,
        source: str | None = None,
        topic: str | None = None,
        subtopic: str | None = None,
    ):
        """Busca documentos com filtros: setor + source + topic + subtopic."""
        store = self._get_store()

        # Monta filtro $and com todos os campos não-nulos
        conditions: list[dict] = [{"sector": sector}]
        if source:
            conditions.append({"source": source})
        if topic:
            conditions.append({"topic": topic})
        if subtopic:
            conditions.append({"subtopic": subtopic})

        where_filter = {"$and": conditions} if len(conditions) > 1 else conditions[0]

        retriever = store.as_retriever(
            search_kwargs={"k": 4, "filter": where_filter}
        )
        docs = retriever.invoke(question)

        context = "\n\n".join(doc.page_content for doc in docs)
        return docs, context

    def _build_prompt(self, context: str, question: str) -> list:
        """Monta as mensagens no formato chat (system + human)."""
        return [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=USER_PROMPT.format(context=context, input=question)),
        ]

    def ask(
        self,
        question: str,
        sector: str,
        source: str | None = None,
        topic: str | None = None,
        subtopic: str | None = None,
    ) -> dict:
        """Faz uma pergunta ao RAG com filtros opcionais."""
        docs, context = self._retrieve(question, sector, source=source, topic=topic, subtopic=subtopic)
        messages = self._build_prompt(context, question)
        response = self._get_llm().invoke(messages)
        return {
            "answer": response.content,
            "sources": [
                {"content": doc.page_content[:300], "metadata": doc.metadata}
                for doc in docs
            ],
        }

    def ask_stream(
        self,
        question: str,
        sector: str,
        source: str | None = None,
        topic: str | None = None,
        subtopic: str | None = None,
    ):
        """Pergunta ao RAG com streaming e filtros opcionais."""
        docs, context = self._retrieve(question, sector, source=source, topic=topic, subtopic=subtopic)
        messages = self._build_prompt(context, question)
        llm = self._get_llm()
        for chunk in llm.stream(messages):
            if chunk.content:
                yield chunk.content
