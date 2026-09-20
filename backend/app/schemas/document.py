from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class DocumentChunkRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    document_id: str
    chunk_index: int
    page_number: int
    section_heading: str
    content: str
    created_at: datetime


class DocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    workspace_id: str
    department_id: Optional[str] = None
    uploaded_by_user_id: Optional[str] = None
    title: str
    original_filename: str
    file_type: str
    file_size_bytes: int
    storage_path: str
    status: str
    error_message: Optional[str] = None
    access_level: str
    page_count: int
    total_chunks: Optional[int] = 0
    created_at: datetime
    updated_at: datetime


class DocumentDetailRead(DocumentRead):
    chunks: List[DocumentChunkRead] = []
    signed_url: Optional[str] = None


class DocumentListResponse(BaseModel):
    items: List[DocumentRead]
    total: int
    page: int
    size: int


class DocumentUploadResponse(BaseModel):
    document: DocumentRead
    message: str
