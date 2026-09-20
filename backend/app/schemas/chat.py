from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class CitationRead(BaseModel):
    id: Optional[str] = None
    document_id: str
    chunk_id: Optional[str] = None
    document_title: str
    page_number: int = 1
    section_heading: str = ""
    relevant_text: str = ""
    confidence: float = 0.0


class MessageRead(BaseModel):
    id: str
    conversation_id: str
    sender_type: str  # USER, ASSISTANT, SYSTEM
    content: str
    created_at: datetime
    sources: List[CitationRead] = Field(default_factory=list)


class ConversationRead(BaseModel):
    id: str
    workspace_id: str
    user_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0


class ConversationDetailRead(BaseModel):
    id: str
    workspace_id: str
    user_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[MessageRead] = Field(default_factory=list)


class ChatQueryRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="The user's query text.")
    conversation_id: Optional[str] = Field(None, description="Existing conversation ID to append message to.")
    department_filter: Optional[str] = Field(None, description="Optional department filter to narrow query within user's authorized scope.")


class ChatQueryResponse(BaseModel):
    conversation_id: str
    user_message_id: str
    assistant_message_id: str
    query: str
    answer: str
    is_grounded: bool
    policy_applied: str = "Grounded Answering Policy"
    citations: List[CitationRead] = Field(default_factory=list)
    latency_ms: float = 0.0
    tokens_used: int = 0
    model_used: str
    grounding_status: str  # "SUFFICIENT" or "REFUSED_INSUFFICIENT_EVIDENCE"


class FeedbackCreateRequest(BaseModel):
    message_id: str
    rating: int = Field(..., ge=-1, le=5, description="Thumbs down (-1), thumbs up (1), or star rating (1-5)")
    category: Optional[str] = Field(None, max_length=50)
    comments: Optional[str] = Field(None, max_length=1000)


class FeedbackReadResponse(BaseModel):
    id: str
    message_id: str
    rating: int
    category: Optional[str] = None
    comments: Optional[str] = None
    status: str = "RECORDED"
