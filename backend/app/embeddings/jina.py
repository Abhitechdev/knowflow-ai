import logging
from typing import List

import httpx

from app.core.config import settings
from app.embeddings.base import BaseEmbeddingProvider

logger = logging.getLogger(__name__)


class JinaEmbeddingProvider(BaseEmbeddingProvider):
    """Jina AI embedding provider (https://api.jina.ai/v1/embeddings) configured to 384 dimensions."""

    def __init__(self, api_key: str = "", model_name: str = "jina-embeddings-v3"):
        self.api_key = api_key or settings.EMBEDDING_API_KEY
        self.model_name = model_name or settings.EMBEDDING_MODEL or "jina-embeddings-v3"
        self._dimension = 384

    @property
    def dimension(self) -> int:
        return self._dimension

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        url = "https://api.jina.ai/v1/embeddings"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        payload = {
            "model": self.model_name,
            "dimensions": self._dimension,
            "normalized": True,
            "embedding_type": "float",
            "input": texts,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            res = await client.post(url, headers=headers, json=payload)
            res.raise_for_status()
            data = res.json()
            sorted_items = sorted(data.get("data", []), key=lambda x: x.get("index", 0))
            return [item["embedding"] for item in sorted_items]

    async def embed_query(self, text: str) -> list[float]:
        results = await self.embed_texts([text])
        return results[0] if results else [0.0] * self._dimension
