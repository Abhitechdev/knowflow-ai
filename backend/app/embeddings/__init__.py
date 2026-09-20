import logging
from typing import Optional

from app.core.config import settings
from app.embeddings.base import BaseEmbeddingProvider

logger = logging.getLogger(__name__)

_embedding_provider: BaseEmbeddingProvider | None = None


def get_embedding_provider() -> BaseEmbeddingProvider:
    """Returns the singleton embedding provider based on application configuration."""
    global _embedding_provider
    if _embedding_provider is not None:
        return _embedding_provider

    provider_type = (settings.EMBEDDING_PROVIDER or "local").lower().strip()

    if provider_type == "openai" and settings.EMBEDDING_API_KEY:
        try:
            from app.embeddings.openai import OpenAIEmbeddingProvider
            logger.info("Using OpenAIEmbeddingProvider (384 dimensions)")
            _embedding_provider = OpenAIEmbeddingProvider()
            return _embedding_provider
        except Exception as e:
            logger.warning(f"Failed to initialize OpenAIEmbeddingProvider: {e}. Falling back to LocalEmbeddingProvider.")

    from app.embeddings.local import LocalEmbeddingProvider
    logger.info("Using LocalEmbeddingProvider (fastembed BAAI/bge-small-en-v1.5, 384 dimensions)")
    _embedding_provider = LocalEmbeddingProvider(model_name=settings.EMBEDDING_MODEL or "BAAI/bge-small-en-v1.5")
    return _embedding_provider
