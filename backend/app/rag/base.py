from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class RankedChunk(BaseModel):
    chunk_id: str
    document_id: str
    document_title: str
    file_type: str = "text"
    page_number: int = 1
    section_heading: str = ""
    content: str
    dense_score: float = 0.0
    sparse_score: float = 0.0
    rrf_score: float = 0.0
    rerank_score: float = 0.0
    department_id: Optional[str] = None
    access_level: str = "WORKSPACE"


class RetrievalResult(BaseModel):
    query: str
    chunks: List[RankedChunk] = Field(default_factory=list)
    dense_count: int = 0
    sparse_count: int = 0


class GroundingAssessment(BaseModel):
    is_sufficient: bool
    confidence_score: float
    reason: str
    policy: str = "Grounded Answering Policy"


class CitationItem(BaseModel):
    document_id: str
    chunk_id: Optional[str] = None
    document_title: str
    page_number: int = 1
    section_heading: str = ""
    relevant_text: str = ""
    confidence: float = 0.0


class RAGResponse(BaseModel):
    answer: str
    is_grounded: bool
    grounding_status: str = "VERIFIED"
    policy_applied: str = "Grounded Answering Policy"
    citations: List[CitationItem] = Field(default_factory=list)
    model_used: str
    latency_ms: float = 0.0
    tokens_used: int = 0
    grounding_assessment: GroundingAssessment
