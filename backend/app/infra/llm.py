"""Fabrica compartilhada de LLM — evita duplicacao de configuracao."""

import logging
from langchain_ollama import ChatOllama
from app.config import settings

logger = logging.getLogger(__name__)


class LLMFactory:
    """Cria (ou reusa) instancias de ChatOllama.

    Cacheia por temperatura para evitar recriar.
    Se quiser forcar recriacao (ex: .env mudou), chame LLMFactory.reset().
    """

    _instances: dict[str, ChatOllama] = {}

    @classmethod
    def get_llm(cls, temperature: float = 0.3, model: str | None = None) -> ChatOllama:
        model = model or settings.llm_model
        key = f"{model}:{temperature}"
        if key not in cls._instances:
            logger.info(
                "Criando ChatOllama: model=%s, base_url=%s, temperature=%s",
                model, settings.ollama_base_url, temperature,
            )
            cls._instances[key] = ChatOllama(
                model=model,
                base_url=settings.ollama_base_url,
                temperature=temperature,
                num_predict=512,          # limita tokens gerados
                timeout=60,               # timeout HTTP de 60s
            )
        return cls._instances[key]

    @classmethod
    def reset(cls):
        """Limpa o cache — util em testes ou reload de config."""
        cls._instances.clear()
