import asyncio
import logging

from fastembed import TextEmbedding

from app.embeddings.base import BaseEmbeddingProvider

logger = logging.getLogger(__name__)


class LocalEmbeddingProvider(BaseEmbeddingProvider):
    """Local ONNX-based embedding provider using fastembed (BAAI/bge-small-en-v1.5, 384 dim)."""

    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        self.model_name = model_name
        logger.info(f"Initializing LocalEmbeddingProvider with model: {model_name}")
        self._model = TextEmbedding(model_name=model_name)
        self._dimension = 384

    @property
    def dimension(self) -> int:
        return self._dimension

    def _sync_embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        embeddings_generator = self._model.embed(texts)
        return [list(emb) for emb in embeddings_generator]

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        return await asyncio.to_thread(self._sync_embed_texts, texts)

    async def embed_query(self, text: str) -> list[float]:
        results = await self.embed_texts([text])
        return results[0] if results else [0.0] * self._dimension
