from abc import ABC, abstractmethod


class BaseEmbeddingProvider(ABC):
    """Abstract base class for embedding providers."""

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Returns the embedding vector dimension."""

    @abstractmethod
    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Generates embeddings for a list of text chunks."""

    @abstractmethod
    async def embed_query(self, text: str) -> list[float]:
        """Generates an embedding for a search query string."""
