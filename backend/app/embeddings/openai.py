import logging

from app.core.config import settings
from app.embeddings.base import BaseEmbeddingProvider

logger = logging.getLogger(__name__)


class OpenAIEmbeddingProvider(BaseEmbeddingProvider):
    """OpenAI embedding provider using text-embedding-3-small configured to 384 dimensions."""

    def __init__(self, api_key: str = "", model_name: str = "text-embedding-3-small"):
        self.api_key = api_key or settings.EMBEDDING_API_KEY
        self.model_name = model_name
        self._dimension = 384
        try:
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError("openai package is required for OpenAIEmbeddingProvider. Install via pip install openai.")

    @property
    def dimension(self) -> int:
        return self._dimension

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        response = await self.client.embeddings.create(
            input=texts,
            model=self.model_name,
            dimensions=self._dimension,
        )
        return [item.embedding for item in response.data]

    async def embed_query(self, text: str) -> list[float]:
        results = await self.embed_texts([text])
        return results[0] if results else [0.0] * self._dimension
