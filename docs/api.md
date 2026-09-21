# KnowFlow AI — API Reference & Schema Documentation

The KnowFlow AI REST API conforms to the OpenAPI 3.1 specification. The interactive documentation is available at `/docs` (Swagger UI) and `/redoc` (ReDoc) on any running instance.

---

## 1. Authentication & Headers

All protected endpoints require a standard Bearer JWT:
```http
Authorization: Bearer <SUPABASE_JWT_ACCESS_TOKEN>
```

---

## 2. Core Endpoint Specifications

### 2.1 Health & Diagnostics

#### `GET /api/health`
System diagnostic returning database connectivity, auth configuration, and service status.
- **Response (200 OK)**:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "environment": "production",
  "database": {
    "status": "healthy",
    "connected": true,
    "message": "Database connection verified."
  },
  "auth": {
    "provider": "supabase",
    "configured": true,
    "url": "https://<project-ref>.supabase.co"
  },
  "timestamp": "2026-09-21T15:00:00.000000+00:00"
}
```

#### `GET /api/health/live`
Fast liveness probe for container orchestrators.
- **Response (200 OK)**: `{"status": "alive"}`

#### `GET /api/health/ready`
Readiness probe verifying DB connectivity before accepting customer traffic.
- **Response (200 OK)**: `{"ready": true, "database": true}`

---

### 2.2 Documents Management

#### `POST /api/v1/documents/upload`
Uploads a document file to Supabase Storage and triggers background extraction, chunking, and embedding.
- **Content-Type**: `multipart/form-data`
- **Fields**:
  - `file`: Binary file (PDF, DOCX, TXT, MD, CSV $\le 25\text{MB}$)
  - `title` (optional): Display name
  - `department_id` (optional): Department UUID
  - `access_level`: `WORKSPACE` | `INTERNAL` | `CONFIDENTIAL` | `RESTRICTED`
- **Response (201 Created)**:
```json
{
  "document": {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "workspace_id": "ws-default-001",
    "title": "Cleanroom Excursion SOP",
    "file_type": "txt",
    "status": "PROCESSING",
    "access_level": "WORKSPACE",
    "page_count": 0,
    "total_chunks": 0
  },
  "message": "Document uploaded successfully. Processing initiated."
}
```

#### `GET /api/v1/documents`
List documents in the current user's workspace with pagination and status.
- **Response (200 OK)**: `{"items": [...], "total": 1, "page": 1, "size": 20}`

#### `GET /api/v1/documents/{document_id}`
Get document metadata, chunk list, and temporary signed download URL.

#### `DELETE /api/v1/documents/{document_id}`
Hard delete a document, cascading deletion to all chunks, embeddings, permissions, and cloud storage blobs.
- **Response (204 No Content)**

---

### 2.3 Grounded Chat & RAG

#### `POST /api/v1/chat/query`
Executes grounded question answering against authorized documents in the user's workspace.
- **Request Body**:
```json
{
  "message": "What is the cleanroom temperature limit?",
  "conversation_id": null
}
```
- **Response (200 OK)**:
```json
{
  "conversation_id": "c1a2b3c4-d5e6-7f8a-9b0c-1d2e3f4a5b6c",
  "message_id": "m1a2b3c4-d5e6-7f8a-9b0c-1d2e3f4a5b6c",
  "content": "According to SOP-QA-901, cleanroom temperature must be maintained strictly between 18.0 C and 22.0 C.",
  "citations": [
    {
      "document_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "document_title": "Cleanroom Excursion SOP",
      "section_heading": "SECTION 2: CRITICAL LIMITS",
      "page_number": 1,
      "snippet": "Cleanroom temperature must be maintained strictly between 18.0 C and 22.0 C."
    }
  ],
  "is_grounded": true
}
```

---

### 2.4 Hybrid Search

#### `GET /api/v1/search`
Query document chunks via dense + sparse hybrid search with RRF reranking.
- **Query Parameters**:
  - `query` (string, required): Search terms
  - `top_k` (int, default: 10): Max results
- **Response (200 OK)**:
```json
{
  "query": "cleanroom temperature",
  "total_results": 1,
  "latency_ms": 142.5,
  "results": [
    {
      "chunk_id": "ch-12345",
      "document_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "document_title": "Cleanroom Excursion SOP",
      "section_heading": "SECTION 2: CRITICAL LIMITS",
      "snippet": "Cleanroom temperature must be maintained strictly between 18.0 C and 22.0 C...",
      "relevance_pct": 94
    }
  ]
}
```
