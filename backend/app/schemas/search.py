from pydantic import BaseModel, Field


class SearchChunkResult(BaseModel):
    chunk_id: str
    document_id: str
    document_title: str
    file_type: str = "text"
    page_number: int = 1
    section_heading: str = ""
    snippet: str
    dense_score: float = 0.0
    sparse_score: float = 0.0
    rrf_score: float = 0.0
    relevance_pct: int = 0


class SearchResponse(BaseModel):
    query: str
    total_results: int
    results: list[SearchChunkResult] = Field(default_factory=list)
    latency_ms: float = 0.0
